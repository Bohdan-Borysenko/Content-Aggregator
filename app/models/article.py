from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .source import Source 

class Article(Base):
    __tablename__ = "articles"

    # Main fields
    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[Optional[str]] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(unique=True, index=True)
    
    # New fields 
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Connections
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    source: Mapped["Source"] = relationship("Source", back_populates="articles")

    views_count: Mapped[int] = mapped_column(Integer, default=0)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, default=0.0)
    summary: Mapped[Optional[str]] = mapped_column(nullable=True) 