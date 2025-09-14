from sqlalchemy import Column, Integer, String
from app.core.database import Base
from sqlalchemy.orm import relationship
from app.core.security import hash_password, verify_password

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    def set_password(self, password:str):
        self.hashed_password= hash_password(password)

    
    role = Column(String(20), default="user", nullable=False)
    posts = relationship("Post", back_populates="author")

    comments = relationship("Comment", back_populates="author", cascade= "all, delete")
                                      