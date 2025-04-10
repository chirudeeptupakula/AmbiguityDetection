from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)

class UserSession(Base):
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    sample_size = Column(Integer)
    sample_count = Column(Integer)
    responses = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

class UserResponse(Base):
    __tablename__ = 'user_responses'

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    image_name = Column(String, nullable=False)
    question1 = Column(String, nullable=False)
    question2 = Column(String, nullable=False)
    question3 = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
