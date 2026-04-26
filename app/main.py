from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional

from app.db.session import get_db, engine
from app.models.source import Source 
from app.models.article import Article 
from app.models.base import Base
from app.schemas.source import SourceCreate, SourceResponse
from app.core.logger import logger 
from celery_tasks.tasks import parse_single_source

app = FastAPI(title="Content Aggregator")

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/sources/", response_model=SourceResponse, tags=["Sources"])
async def create_source(source_data: SourceCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"Creating a new source: {source_data.url}")
    new_source = Source(
        name=source_data.name,
        url=source_data.url,
        source_type=source_data.source_type
    )
    db.add(new_source)
    await db.commit()
    await db.refresh(new_source)
    return new_source

@app.post("/sources/{source_id}/fetch", tags=["Sources"])
async def fetch_articles_manually(source_id: int, db: AsyncSession = Depends(get_db)):
    logger.info(f"Manually start background parsing for an ID: {source_id}")
    result = await db.execute(select(Source).where(Source.id == source_id))
    source = result.scalars().first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    task = parse_single_source.delay(source_id)
    return {"status": "accepted", "task_id": task.id, "message": "Parsing started in background"}

# --- ARTICLES  ---

@app.get("/articles/", tags=["Articles"])
async def get_articles(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Search by title or text"),
    min_sentiment: Optional[float] = Query(None, description="Minimum pitch threshold (-1.0 до 1.0)"),
    limit: int = 20,
    offset: int = 0
):
    logger.info(f"Request articles: search={search}, min_sentiment={min_sentiment}")
    stmt = select(Article)
    
    # 1. Search
    if search:
        stmt = stmt.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%")
            )
        )
    
    # 2. Filter by mood
    if min_sentiment is not None:
        stmt = stmt.where(Article.sentiment_score >= min_sentiment)
    
    # 3. Sorting and pagination
    stmt = stmt.order_by(Article.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()