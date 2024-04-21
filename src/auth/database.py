from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# SQLALCHEMY_DATABASE_URL = "sqlite:///./auth_db.db"
SQLALCHEMY_DATABASE_URL = os.environ.get("DB_URI", None)
if not SQLALCHEMY_DATABASE_URL:
    raise Exception("set DB_URI in your environment")

if not SQLALCHEMY_DATABASE_URL:
    raise Exception("set DATABASE_URL in your environment")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()