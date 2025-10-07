import os
import random
import json
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load the database URL from the .env file
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable not found in .env file.")

engine = create_engine(DATABASE_URL)
print("Connecting to Postgres database...")

# --- Data Generation Functions ---
fake = Faker('en_IN')
INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Chennai", "Kolkata", "Hyderabad", "Jaipur", "Goa",
    "Kochi", "Ahmedabad", "Pune", "Agra", "Varanasi", "Udaipur", "Shimla", "Rishikesh",
    "Amritsar", "Jodhpur", "Mysuru", "Darjeeling", "Lucknow", "Nagpur", "Indore", "Patna"
]
INDIAN_AIRLINES = ["IndiGo", "Air India", "Vistara", "SpiceJet", "Akasa Air", "Air India Express"]
INDIAN_BUS_OPERATORS = ["Sharma Travels", "VRL Logistics", "RedBus Express", "ZingBus", "IntrCity SmartBus", "Prasanna Purple"]

def generate_flights(n=1000):
    data = []
    for i in range(n):
        origin, destination = random.sample(INDIAN_CITIES, 2)
        departure = fake.date_time_between(start_date="+1d", end_date="+60d")
        duration = random.randint(50, 240)
        arrival = departure + timedelta(minutes=duration)
        data.append({
            "flight_id": f"FL{10000 + i}", "airline": random.choice(INDIAN_AIRLINES),
            "origin": origin, "destination": destination, "departure_time": departure,
            "arrival_time": arrival, "duration_minutes": duration,
            "price_inr": random.randint(2500, 18000), "seats_available": random.randint(2, 80)
        })
    return pd.DataFrame(data)

def generate_hotels(n=800):
    data = []
    amenities_list = ["Free WiFi", "Swimming Pool", "Restaurant", "Gym", "Free Parking", "Spa", "Room Service"]
    for i in range(n):
        city = random.choice(INDIAN_CITIES)
        amenities = random.sample(amenities_list, k=random.randint(2, 6))
        data.append({
            "hotel_id": f"HT{1000 + i}", "hotel_name": f"{fake.company()} Palace",
            "city": city, "address": fake.street_address(),
            "star_rating": round(random.uniform(2.5, 5.0), 1),
            "price_per_night_inr": random.randint(800, 25000),
            "amenities": json.dumps(amenities), "available_rooms": random.randint(0, 40)
        })
    return pd.DataFrame(data)

def generate_trains(n=500):
    data = []
    for i in range(n):
        origin, destination = random.sample(INDIAN_CITIES, 2)
        departure = fake.date_time_between(start_date="+1d", end_date="+60d")
        duration = random.randint(300, 2200) # Trains have longer journeys
        arrival = departure + timedelta(minutes=duration)
        data.append({
            "train_id": f"TR{12000 + i}", "train_name": f"{origin.split(' ')[0]}-{destination.split(' ')[0]} Superfast",
            "origin": origin, "destination": destination, "departure_time": departure,
            "arrival_time": arrival, "price_SL_inr": random.randint(400, 1200),
            "price_3A_inr": random.randint(1000, 3000), "price_2A_inr": random.randint(1500, 5000),
            "seats_available_2A": random.randint(5, 100)
        })
    return pd.DataFrame(data)

def generate_buses(n=600):
    data = []
    bus_types = ["AC Sleeper", "Non-AC Seater", "AC Seater", "Volvo Multi-Axle"]
    for i in range(n):
        origin, destination = random.sample(INDIAN_CITIES, 2)
        departure = fake.date_time_between(start_date="+1d", end_date="+15d")
        duration = random.randint(180, 1500)
        arrival = departure + timedelta(minutes=duration)
        data.append({
            "bus_id": f"BUS{8000 + i}", "operator": random.choice(INDIAN_BUS_OPERATORS),
            "bus_type": random.choice(bus_types), "origin": origin, "destination": destination,
            "departure_time": departure, "arrival_time": arrival,
            "price_inr": random.randint(300, 2500), "seats_available": random.randint(1, 35)
        })
    return pd.DataFrame(data)

def generate_attractions(n=400):
    data = []
    categories = ["Historical Monument", "Nature & Parks", "Museum", "Religious Site", "Shopping District"]
    for i in range(n):
        data.append({
            "attraction_id": f"AT{2000 + i}", "attraction_name": f"{fake.company()} Point",
            "city": random.choice(INDIAN_CITIES), "category": random.choice(categories),
            "description": fake.paragraph(nb_sentences=4),
            "entry_fee_inr": random.choice([0, 20, 50, 100, 250, 500]),
            "opening_hours": "10:00 AM - 6:00 PM"
        })
    return pd.DataFrame(data)

def create_and_populate_tables():
    """Defines the schema and populates all tables in Postgres."""
    print("Starting table creation and population...")
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY, name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL, password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.commit()
        print("Table 'users' is ready.")

        table_populators = {
            'flights': generate_flights,
            'hotels': generate_hotels,
            'trains': generate_trains,
            'buses': generate_buses,
            'attractions': generate_attractions
        }

        for table_name, populator_func in table_populators.items():
            print(f"Generating data for '{table_name}'...")
            df = populator_func()
            df.to_sql(table_name, engine, if_exists='replace', index=False)
            print(f"-> Populated '{table_name}' with {len(df)} records.")

# --- Main Execution ---
if __name__ == "__main__":
    create_and_populate_tables()
    print("\n✅ Database migration complete!")