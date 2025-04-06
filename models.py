from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sample_size = db.Column(db.Integer)
    sample_count = db.Column(db.Integer)
    responses = db.Column(db.JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
