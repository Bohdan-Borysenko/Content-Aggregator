import asyncio
import os
import httpx
from sqlalchemy import select
from .main import celery_app
from app.db.session import AsyncSessionLocal 
from app.services.parser import fetch_rss_articles
from app.services.nlp import analyze_sentiment 
from app.models.source import Source
from app.models.article import Article
from app.core.logger import logger 

HF_TOKEN = os.getenv("HF_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

# Limiting the number of concurrent requests to the AI
ai_semaphore = asyncio.Semaphore(3)

async def summarize_text(text: str) -> str:
    if not HF_TOKEN or not text or len(text) < 50:
        return text[:150] + "..." if text else "No content"

    async with ai_semaphore:
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        payload = {
            "inputs": text[:1024], 
            "parameters": {"max_length": 60, "min_length": 20, "do_sample": False}
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(HF_API_URL, headers=headers, json=payload, timeout=25.0)
                
                if response.status_code == 200:
                    result = response.json()
                    return result[0].get('summary_text', text[:150] + "...")
                elif response.status_code == 503:
                    logger.info("AI Model is loading, returning fallback summary")
                    return text[:150] + "..."
                else:
                    logger.warning(f"AI API error {response.status_code}")
                    return text[:150] + "..."
                    
        except Exception as e:
            logger.error(f"AI Request failed: {e}")
            return text[:150] + "..."

async def update_sources_logic(source_id: int = None):
    async with AsyncSessionLocal() as db:
        try:
            if source_id:
                stmt = select(Source).where(Source.id == source_id)
            else:
                stmt = select(Source)
            
            result = await db.execute(stmt)
            sources = result.scalars().all()
            
            if not sources:
                logger.warning("Источники не найдены.")
                return

            for source in sources:
                try:
                    logger.info(f"Парсинг: {source.name}")
                    articles_data = await fetch_rss_articles(source.url)
                    
                    saved_count = 0
                    for data in articles_data:
                        check_stmt = select(Article).where(Article.url == data["url"])
                        exists_res = await db.execute(check_stmt)
                        
                        if not exists_res.scalars().first():
                            # Sentiment 
                            full_text = f"{data['title']} {data.get('content', '')}"
                            sentiment = analyze_sentiment(full_text)
                            
                            # Summary 
                            text_for_ai = data.get('content') or data.get('title')
                            ai_summary = await summarize_text(text_for_ai)
                            
                            new_art = Article(
                                title=data["title"],
                                url=data["url"],
                                content=data["content"],
                                source_id=source.id,
                                sentiment_score=sentiment, 
                                summary=ai_summary
                            )
                            db.add(new_art)
                            saved_count += 1
                    
                    await db.commit()
                    if saved_count > 0:
                        logger.info(f"Добавлено {saved_count} статей из {source.name}")
                
                except Exception as e:
                    logger.error(f"Ошибка источника {source.url}: {e}")
                    await db.rollback()
                    continue
        except Exception as e:
            logger.exception("Критическая ошибка парсинга")
            await db.rollback()
            raise e 

@celery_app.task(
    name="celery_tasks.tasks.parse_single_source",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def parse_single_source(self, source_id: int):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(update_sources_logic(source_id))
    except Exception as exc:
        raise self.retry(exc=exc)

@celery_app.task(
    name="celery_tasks.tasks.update_all_sources",
    bind=True,  
    max_retries=2,
    default_retry_delay=300 
)
def update_all_sources(self):
    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(update_sources_logic())
    except Exception as exc:
        raise self.retry(exc=exc)