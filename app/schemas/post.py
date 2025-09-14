from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
  title: str
  content: str

class PostCreate(PostBase):
  pass

class PostUpdate(BaseModel):
  title: Optional[str] = None
  content: Optional[str] = None

class PostResponse(PostBase):
  id: int
  author_id: int
  file_path: Optional[str]  
  created_at: datetime

  model_config = {
    "from_attributes": True,
    "strict": True
    }

  