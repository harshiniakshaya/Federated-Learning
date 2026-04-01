from fastapi import FastAPI
import psycopg2
import pickle
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

app2 = FastAPI()

app2.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CENTRAL DB CONNECTION 
# This connects ONLY to the Model Hub
CENTRAL_DB_PARAMS = {
    "host": os.getenv("CENTRAL_DB_HOST"),
    "database": os.getenv("CENTRAL_DB_NAME"),
    "user": os.getenv("CENTRAL_DB_USER"),
    "password": os.getenv("CENTRAL_DB_PASSWORD"),
    "sslmode": "require"
}

HOSPITAL_ID = "hospitalA" # Change to "hospitalb" for the other node

@app2.post("/push_to_central")
def push_to_central():
    try:
        with open(f"{HOSPITAL_ID}_model.pkl", "rb") as f:
            model_bytes = f.read()

        conn = psycopg2.connect(**CENTRAL_DB_PARAMS)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {HOSPITAL_ID} (
                id SERIAL PRIMARY KEY,
                model_data BYTEA NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Insert model
        cursor.execute(
            f"INSERT INTO {HOSPITAL_ID} (model_data) VALUES (%s)",
            (psycopg2.Binary(model_bytes),)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "Local model pushed to Central DB"}

    except FileNotFoundError:
        return {"error": "Local model file not found. Run /train_local in app.py first."}

    except Exception as e:
        return {"error": str(e)}

@app2.get("/pull_from_central")
def pull_from_central():
    """Downloads the aggregated global model to initial_model.pkl"""
    try:
        conn = psycopg2.connect(**CENTRAL_DB_PARAMS)
        cursor = conn.cursor()
        
        # Get the one record from the aggregated table
        cursor.execute("SELECT model_data FROM aggregated ORDER BY updated_at DESC LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            return {"error": "Aggregated model not found in central-db"}

        # Overwrite the starting model for app.py
        with open("initial_model.pkl", "wb") as f:
            f.write(row[0])
            
        cursor.close()
        conn.close()
        return {"status": "Global model pulled. app.py is now ready for a new training round."}
    except Exception as e:
        return {"error": str(e)}