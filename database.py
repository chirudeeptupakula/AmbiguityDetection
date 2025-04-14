# database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

db_url = "postgresql://postgres:1234@localhost:5432/etl_pipeline_db"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()
