import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Try to load DATABASE_URL from environment, fallback to local for development
db_url = os.environ.get(
    "DATABASE_URL",

   # "postgresql://postgres:1306@localhost:5432/etl_pipeline_db"
    "postgresql://chiru1306:g6CkpnXoDupva30fuXK2MtL2yBCSCSYn@dpg-cvujh53uibrs738ascn0-a:5432/webapp_db_recf"


)

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()
