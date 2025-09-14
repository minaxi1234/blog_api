from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User

db: Session = SessionLocal()

email_to_update = "meenakshi@example.com"
user = db.query(User).filter(User.email == email_to_update).first()
if user:
  print(f"Before update: {user.username} role = {user.role}")
  user.role = "admin"
  db.commit()
  print(f"After update: {user.username} role = {user.role}")

else:
  print(f"No user found with email { email_to_update}")

  db.close()

