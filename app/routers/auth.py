from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.database import get_db
from app.core.security import verify_password, hash_password, create_access_token
from app.schemas.user import UserCreate, UserResponse,UserLogin
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session= Depends(get_db)):
  existing_user = db.query(User).filter(User.email == user.email).first()
  if existing_user:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= "Email already registered")

  user_count = db.query(User).count()

  role = "admin" if user_count == 0 else "user"
  
  new_user=User(
    username = user.username,
    email = user.email,
    hashed_password= hash_password(user.password),
    role= role
  )

  db.add(new_user)
  db.commit()
  db.refresh(new_user)

  return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
  db_user = db.query(User).filter(User.email == user.email).first()
  if not db_user:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
  
  if not verify_password(user.password, db_user.hashed_password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
  access_token = create_access_token({"sub": db_user.email})
  return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
  return {
    "id": current_user.id,
    "username": current_user.username,
    "email": current_user.email
  }



