from app import app, db
from flask import request, jsonify, render_template
from models import User, UserSession
import analysis  # call analysis.py from here

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username'], password=data['password']).first()
    if user:
        return jsonify({"message": "Login successful!", "user_id": user.id})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/generate_samples', methods=['POST'])
def generate_samples():
    data = request.json
    user_id = data['user_id']
    sample_size = data['sample_size']
    sample_count = data['sample_count']

    # Call analysis with user-defined inputs
    analysis.generate_multiple_samples(sample_size=sample_size, iterations=sample_count)

    session = UserSession(
        user_id=user_id,
        sample_size=sample_size,
        sample_count=sample_count,
        responses={}
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({"message": "Samples generated!"})
