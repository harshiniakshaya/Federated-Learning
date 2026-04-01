from fastapi import FastAPI
import psycopg2
import pickle
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


CENTRAL_DB = {
    "host": os.getenv("CENTRAL_DB_HOST"),
    "database": os.getenv("CENTRAL_DB_NAME"),
    "user": os.getenv("CENTRAL_DB_USER"),
    "password": os.getenv("CENTRAL_DB_PASSWORD"),
    "sslmode": "require"
}


@app.post("/aggregate")
def run_aggregation():

    conn = psycopg2.connect(**CENTRAL_DB)
    cursor = conn.cursor()

    models = []

    # Fetch latest models from both hospitals
    for table in ["hospitala", "hospitalb"]:

        cursor.execute(
            f"SELECT model_data FROM {table} ORDER BY updated_at DESC LIMIT 1"
        )

        row = cursor.fetchone()

        if row:
            models.append(pickle.loads(row[0]))

    if len(models) < 2:
        cursor.close()
        conn.close()
        return {"error": "Missing models from hospitals"}

    # Federated Averaging
    avg_coef = np.mean([m['model'].coef_ for m in models], axis=0)
    avg_intercept = np.mean([m['model'].intercept_ for m in models], axis=0)

    global_assets = models[0]

    global_assets['model'].coef_ = avg_coef
    global_assets['model'].intercept_ = avg_intercept

    # Create aggregated table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aggregated (
            id SERIAL PRIMARY KEY,
            model_data BYTEA,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Clear previous global model
    cursor.execute("TRUNCATE TABLE aggregated")

    # Insert new global model
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

    return {"status": "Global model aggregated successfully"}