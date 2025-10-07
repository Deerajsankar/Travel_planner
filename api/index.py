import os
import json
from flask import Flask, g, render_template, request, jsonify # Add render_template
import psycopg2
from psycopg2.extras import RealDictCursor

# --- App Configuration ---
app = Flask(__name__, static_folder='../static', template_folder='../templates')

# --- Database Connection (not used by budget splitter, but kept for main app) ---
def get_db():
    if "db" not in g:
        conn_string = os.environ.get("DATABASE_URL")
        g.db = psycopg2.connect(conn_string)
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# --- Routes for Rendering HTML Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/planner')
def planner():
    return render_template('planner.html')

@app.route('/results')
def results():
    destination = request.args.get('destination', 'Unknown')
    return render_template('results.html', destination=destination)

# --- NEW ROUTES FOR BUDGET SPLITTER ---
@app.route('/budget-setup')
def budget_setup():
    return render_template('budget_setup.html')

@app.route('/budget-expenses')
def budget_expenses():
    return render_template('budget_expenses.html')

# --- API Routes for Travel Data (from your original code) ---
@app.route("/api/flights")
def get_flights():
    # ... Your database query logic for flights ...
    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM flights LIMIT 20;") # Example query
    flights = cursor.fetchall()
    cursor.close()
    return jsonify(flights)

# ... Add your other API endpoints for hotels, trains, etc. here ...