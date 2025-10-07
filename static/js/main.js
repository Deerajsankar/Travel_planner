import os
import json
from flask import Flask, g, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

# --- App Configuration ---
# Correctly points to the static/template folders in the root directory
app = Flask(__name__, static_folder='../static', template_folder='../templates')

# --- Database Connection ---
def get_db():
    if "db" not in g:
        # This securely pulls the DATABASE_URL from Vercel's environment variables
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
    """
    This is the main logic. It gets data from the planner form,
    queries the database, and passes the real data to the results.html template.
    """
    destination = request.args.get('destination', 'Unknown')
    budget = request.args.get('budget', 50000, type=int)

    db = get_db()
    cursor = db.cursor(cursor_factory=RealDictCursor)

    # Fetch hotels in the destination within the budget
    cursor.execute(
        "SELECT * FROM hotels WHERE city ILIKE %s AND price_per_night_inr <= %s LIMIT 10",
        (f'%{destination}%', budget / 5) # Example: budget for 5 nights
    )
    hotels = cursor.fetchall()

    # Fetch flights to the destination
    cursor.execute(
        "SELECT * FROM flights WHERE destination ILIKE %s LIMIT 10",
        (f'%{destination}%',)
    )
    flights = cursor.fetchall()
    
    # Fetch trains to the destination
    cursor.execute(
        "SELECT * FROM trains WHERE destination ILIKE %s LIMIT 10",
        (f'%{destination}%',)
    )
    trains = cursor.fetchall()
    
    # Fetch buses to the destination
    cursor.execute(
        "SELECT * FROM buses WHERE destination ILIKE %s LIMIT 10",
        (f'%{destination}%',)
    )
    buses = cursor.fetchall()

    # Fetch attractions in the destination
    cursor.execute(
        "SELECT * FROM attractions WHERE city ILIKE %s LIMIT 10",
        (f'%{destination}%',)
    )
    attractions = cursor.fetchall()

    cursor.close()

    # Pass all the fetched data to the template
    return render_template(
        'results.html',
        destination=destination,
        hotels=hotels,
        flights=flights,
        trains=trains,
        buses=buses,
        attractions=attractions
    )

# --- Budget Splitter Routes ---
@app.route('/budget-setup')
def budget_setup():
    return render_template('budget_setup.html')

@app.route('/budget-expenses')
def budget_expenses():
    return render_template('budget_expenses.html')