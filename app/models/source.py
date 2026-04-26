from typing import List, TYPE_CHECKING 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from .article import Article 

class Source(Base):
    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    source_type: Mapped[str] = mapped_column(default="rss")

    articles: Mapped[List["Article"]] = relationship("Article", back_populates="source")