import httpx
import feedparser
from typing import List, Dict
from app.core.logger import logger 
from app.schemas.article import ArticleParsed
from pydantic import ValidationError

from app.services.nlp import analyze_sentiment 

async def fetch_rss_articles(url: str) -> List[Dict]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
        try:
            response = await client.get(url, follow_redirects=True)
            
            if response.status_code != 200:
                logger.error(f"Loading error {url}: status {response.status_code}")
                return []

            feed = feedparser.parse(response.text)
            
            if not feed.entries:
                logger.warning(f"An empty RSS feed at: {url}")
                return []

            articles = []
            for entry in feed.entries:
                try:
                    # Extracting data
                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    content = entry.get("summary", entry.get("description", ""))

                    # We analyze the tone based on the headline and summary
                    full_text_for_analysis = f"{title}. {content}"
                    score = analyze_sentiment(full_text_for_analysis)
                    # -------------------------------------

                    # We are validating the article, including our new assessment
                    article_data = ArticleParsed(
                        title=title,
                        url=link,
                        content=content,
                        sentiment_score=score 
                    )
                    
                    articles.append(article_data.model_dump())
                    
                except ValidationError as ve:
                    logger.warning(f"The article was skipped due to a validation error in {url}: {ve.json()}")
                    continue

            logger.info(f"Successfully saved {len(articles)} articles from {url}. The tone analysis is complete.")
            return articles

        except httpx.ConnectError:
            logger.error(f"Unable to connect to the server (DNS/Network): {url}")
            return []
        except Exception as e:
            logger.exception(f"Critical parser failure for {url}")
            return []