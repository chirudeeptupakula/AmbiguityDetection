# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

load_dotenv()  # ⬅️ Load environment variables from .env file

db_url = os.getenv("DATABASE_URL")  # should NOT be None
engine = create_engine(db_url)
Base = declarative_base()
