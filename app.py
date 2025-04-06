from flask import Flask, render_template, request, redirect, url_for, flash, session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from flask import render_template
from analysis import main as generate_images


import subprocess
import json
import os

app = Flask(__name__)
app.secret_key = 'secret123'

# PostgreSQL Connection
db_url = "postgresql://postgres:1234@localhost:5432/etl_pipeline_db"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
db = Session()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

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
    query_check = text("SELECT * FROM users WHERE username = :u OR email = :e")
    exists = db.execute(query_check, {"u": data['username'], "e": data['email']}).fetchone()

    if exists:
        flash("Username or email already exists!", "warning")
        return redirect(url_for('register_form'))

    query = text("""
        INSERT INTO users (username, password, firstname, lastname, email, role, department)
        VALUES (:u, :p, :f, :l, :e, :r, :d)
    """)
    db.execute(query, {
        "u": data['username'],
        "p": data['password'],  # In production, use hashed passwords
        "f": data['firstname'],
        "l": data['lastname'],
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
    return render_template('userInputForm.html')  # 🔁 Renders the form instead of just a welcome text


@app.route('/generate_samples', methods=['POST'])
def generate_samples():
    if 'username' not in session:
        return redirect(url_for('index'))

    # Get user form inputs
    sample_size = int(request.form['sample_size'])
    sample_count = int(request.form['num_samples'])

    # Call the analysis logic
    generate_images(sample_size, sample_count)

    return redirect(url_for('view_images'))  # Define this route to show latest images


@app.route('/view_images')
def view_images():
    visuals_path = os.path.join("static", "visuals.json")

    if os.path.exists(visuals_path):
        with open(visuals_path) as f:
            images = json.load(f)
    else:
        images = []

    return render_template("view_images.html", images=images)


if __name__ == '__main__':
    app.run(debug=True)
