from fastapi import FastAPI
import psycopg2
import pickle
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# APP
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# BASE DIR (for safety, even if not used here)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CENTRAL DB CONFIG
CENTRAL_DB = {
    "host": os.getenv("CENTRAL_DB_HOST"),
    "database": os.getenv("CENTRAL_DB_NAME"),
    "user": os.getenv("CENTRAL_DB_USER"),
    "password": os.getenv("CENTRAL_DB_PASSWORD"),
    "sslmode": "require"
}


# SAFE DB CONNECTION
def get_connection():
    try:
        return psycopg2.connect(**CENTRAL_DB)
    except Exception as e:
        print("Central DB connection error:", e)
        return None


# HEALTH CHECK
@app.get("/")
def health():
    return {"status": "Central server running"}


# AGGREGATION ENDPOINT
@app.post("/aggregate")
def run_aggregation():

    conn = get_connection()
    if conn is None:
        return {"error": "Central DB not connected"}

    try:
        cursor = conn.cursor()
        models = []

        # Fetch latest models from both hospitals
        for table in ["hospitala", "hospitalb"]:
            try:
                cursor.execute(
                    f"SELECT model_data FROM {table} ORDER BY updated_at DESC LIMIT 1"
                )
                row = cursor.fetchone()

                if row:
                    models.append(pickle.loads(row[0]))

            except Exception as table_error:
                print(f"Error reading table {table}:", table_error)

        # Check if both models exist
        if len(models) < 2:
            cursor.close()
            conn.close()
            return {"error": "Missing models from hospitals"}

        # Federated Averaging
        try:
            avg_coef = np.mean([m['model'].coef_ for m in models], axis=0)
            avg_intercept = np.mean([m['model'].intercept_ for m in models], axis=0)
        except Exception as e:
            cursor.close()
            conn.close()
            return {
                "error": "Model aggregation failed",
                "details": str(e)
            }

        # Use first model structure
        global_assets = models[0]

        global_assets['model'].coef_ = avg_coef
        global_assets['model'].intercept_ = avg_intercept

        # Create aggregated table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS aggregated (
                id SERIAL PRIMARY KEY,
                model_data BYTEA,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Clear old model safely
        cursor.execute("TRUNCATE TABLE aggregated")

        # Insert new aggregated model
        cursor.execute(
            """
            INSERT INTO aggregated (model_data, updated_at)
            VALUES (%s, CURRENT_TIMESTAMP)
            """,
            (psycopg2.Binary(pickle.dumps(global_assets)),)
        )

        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "Global model aggregated successfully",
            "models_used": len(models)
        }

    except Exception as e:
        return {
            "error": "Aggregation failed",
            "details": str(e)
        }