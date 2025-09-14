from sqlalchemy import Column, Integer, String, Text,ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Post(Base):
  __tablename__ = "posts"

  id = Column(Integer, primary_key=True, index=True)
  title = Column(String(200), nullable=False)
  content = Column(Text, nullable=False)
  created_at = Column(DateTime(timezone=True), server_default=func.now())
  file_path = Column(String, nullable = True)
  author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

  author = relationship("User", back_populates= "posts")

  comments = relationship("Comment", back_populates="post", cascade="all, delete")

  
