from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

def hash_password(password: str) -> str:
  return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: int =None):
  to_encode = data.copy()
  if expires_delta:
    expires = datetime.utcnow() + timedelta(minutes=expires)
  else:
    expires = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expires})
  encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
  return encoded_jwt