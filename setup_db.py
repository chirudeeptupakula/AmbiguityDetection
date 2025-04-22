# setup_db.py

from database import engine
from models import Base

# This will create all tables defined in models.py
Base.metadata.create_all(engine)

print("✅ All tables created successfully on Render PostgreSQL.")
