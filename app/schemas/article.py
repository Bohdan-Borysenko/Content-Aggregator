from pydantic import BaseModel, HttpUrl, Field
from typing import Optional

class ArticleParsed(BaseModel):
    title: str = Field(..., min_length=1)
    url: HttpUrl  
    content: Optional[str] = None

class ArticleCreate(ArticleParsed):
    source_id: int

class ArticleParsed(BaseModel):
    title: str = Field(..., min_length=1)
    url: str 
    content: Optional[str] = None
    sentiment_score: float = 0.0  