from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional
from app.db.session import get_db
from app.models.article import Article
from app.schemas.article import ArticleOut

router = APIRouter()

@router.get("/", response_model=List[ArticleOut])
async def get_articles(
    db: AsyncSession = Depends(get_db),
    search: Optional[str] = Query(None, description="Поиск по заголовку или тексту"),
    min_sentiment: Optional[float] = Query(None, description="Минимальный порог тональности (-1.0 до 1.0)"),
    source_id: Optional[int] = None,
    limit: int = 20,
    offset: int = 0
):
    stmt = select(Article)
    
    # Filter by source
    if source_id:
        stmt = stmt.where(Article.source_id == source_id)
    
    # Full-text search
    if search:
        stmt = stmt.where(
            or_(
                Article.title.ilike(f"%{search}%"),
                Article.content.ilike(f"%{search}%")
            )
        )
    
    # Filter by mood
    if min_sentiment is not None:
        stmt = stmt.where(Article.sentiment_score >= min_sentiment)
    
    # Sort by: Latest news 
    stmt = stmt.order_by(Article.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    return result.scalars().all()