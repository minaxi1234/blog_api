from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from app.core.config import settings


Base = declarative_base()

engine = create_engine(settings.DATABASE_URL, connect_args= {"check_same_thread": False})

SessionLocal = sessionmaker(autoflush= False, autocommit= False, bind= engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

