from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
  username: str
  email: EmailStr
  password: str 
  role:str

class UserResponse(BaseModel):
  id: int
  username: str
  email: EmailStr
  role:str

class UserLogin(BaseModel):
  email: EmailStr
  password: str

  model_config = {
    "from_attributes": True,
    "strict": True
    }