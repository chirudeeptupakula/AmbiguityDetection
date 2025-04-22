from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from sqlalchemy.orm import Session as DBSession
from analysis import main as generate_images
from models import UserResponse
from database import engine

import json
import os

app = Flask(__name__)
app.secret_key = 'secret123'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with DBSession(bind=engine) as db:
        query = text("SELECT * FROM users WHERE username = :u AND password = :p")
        user = db.execute(query, {"u": username, "p": password}).fetchone()

    if user:
        session['username'] = username
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid username or password.", "danger")
        return redirect(url_for('index'))

@app.route('/register')
def register_form():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.form

    with DBSession(bind=engine) as db:
        query_check = text("SELECT * FROM users WHERE username = :u OR email = :e")
        exists = db.execute(query_check, {"u": data['username'], "e": data['email']}).fetchone()

        if exists:
            flash("Username or email already exists!", "warning")
            return redirect(url_for('register_form'))

        query = text("""
            INSERT INTO users (username, password, first_name, last_name, email, role, department)
            VALUES (:u, :p, :f, :l, :e, :r, :d)
        """)
        db.execute(query, {
            "u": data['username'],
            "p": data['password'],  # In production, use hashed passwords
            "f": data['first_name'],
            "l": data['last_name'],
            "e": data['email'],
            "r": data['role'],
            "d": data['department']
        })
        db.commit()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Login required.", "danger")
        return redirect(url_for('index'))
    return render_template('userInputForm.html')

@app.route('/generate_samples', methods=['POST'])
def generate_samples():
    if 'username' not in session:
        return redirect(url_for('index'))

    sample_size = int(request.form['sample_size'])
    sample_count = int(request.form['num_samples'])

    generate_images(sample_size, sample_count)

    return redirect(url_for('view_images'))

@app.route('/view_images')
def view_images():
    visuals_path = os.path.join("static", "visuals.json")

    if os.path.exists(visuals_path):
        with open(visuals_path) as f:
            images = json.load(f)
    else:
        images = []

    return render_template("view_images.html", images=images)

@app.route('/submit_response', methods=['POST'])
def submit_response():
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    form = request.form

    responses = []
    index = 0

    while f'image_name_{index}' in form:
        response = UserResponse(
            username=username,
            image_name=form[f'image_name_{index}'],
            question1=form.get(f'question1_{index}'),
            question2=form.get(f'question2_{index}'),
            question3=form.get(f'question3_{index}')
        )
        responses.append(response)
        index += 1

    with DBSession(bind=engine) as db:
        db.add_all(responses)
        db.commit()

    flash("All responses submitted!", "success")
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')


if __name__ == '__main__':
    app.run(debug=True)
