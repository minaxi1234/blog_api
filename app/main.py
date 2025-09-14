from fastapi import FastAPI, status
from fastapi.responses import  JSONResponse
from app.routers import auth, posts, comments
from sqlalchemy import text
import logging
from app.core.middleware import LoggingMiddleware,setup_cors, RateLimiterMiddleware
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.database import Base, engine
from app.models import user, post, comment
from fastapi.staticfiles import StaticFiles

app= FastAPI()
Base.metadata.create_all(bind=engine)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


setup_cors(app)


logging.basicConfig(level=logging.INFO)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimiterMiddleware, max_requests= 5, window_seconds = 60)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/")
def read_root():
  return{"message": "Hello, Meenakshi! your Blog API is ready."}

@app.get("/health")
def health_check():
  app_status = "ok"

  db_status = "ok"
  error_msg = None
  db = None

  try:
    db = next(get_db())
    db.execute(text("SELECT 1"))
  except Exception as e:
    db_status = "down"
    error_msg = str(e)
  finally:
    try:
      if db is not None:
        db.close()
    except Exception:
      pass

  body = {"status":app_status, "database": db_status}
  if db_status == "down":
    body["error"] = error_msg
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=body)
  return body
  

@app.on_event("startup")
async def startup_db_check():
  try:
    db = next(get_db())
    db.execute(text("SELECT 1"))
    print("Database connected successfully!")
  except Exception as e:
    print("Database connection failed:", e)

@app.on_event("shutdown")
async def shutdown_event():
  print("Application is shutting down... cleaning up resources.")

