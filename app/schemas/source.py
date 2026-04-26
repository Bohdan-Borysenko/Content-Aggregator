from pydantic import BaseModel, HttpUrl

class SourceCreate(BaseModel):
    name: str
    url: str  
    source_type: str = "rss"

class SourceResponse(SourceCreate):
    id: int
    
    class Config:
        from_attributes = True 