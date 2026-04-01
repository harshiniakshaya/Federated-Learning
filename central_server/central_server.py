import psycopg2
import pickle
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

CENTRAL_DB = {
    "host": os.getenv("CENTRAL_DB_HOST"),
    "database": os.getenv("CENTRAL_DB_NAME"),
    "user": os.getenv("CENTRAL_DB_USER"),
    "password": os.getenv("CENTRAL_DB_PASSWORD"),
    "sslmode": "require"
}

def run_aggregation():
    conn = psycopg2.connect(**CENTRAL_DB)
    cursor = conn.cursor()

    # Create aggregated table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS aggregated (
            id SERIAL PRIMARY KEY,
            model_data BYTEA NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 1. Pull latest from A and B
    models = []
    for table in ["hospitala", "hospitalb"]:
        cursor.execute(f"SELECT model_data FROM {table} ORDER BY updated_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            models.append(pickle.loads(row[0]))

    if len(models) < 2:
        print("Missing data from one or more hospitals.")
        return

    # 2. Federated Averaging Math
    avg_coef = np.mean([m['model'].coef_ for m in models], axis=0)
    avg_intercept = np.mean([m['model'].intercept_ for m in models], axis=0)

    # 3. Create Global Model Object
    global_assets = models[0] # Template
    global_assets['model'].coef_ = avg_coef
    global_assets['model'].intercept_ = avg_intercept

    # 4. Clear 'aggregated' table and store the one true record
    cursor.execute("TRUNCATE TABLE aggregated")
    cursor.execute(
        "INSERT INTO aggregated (model_data) VALUES (%s)",
        (psycopg2.Binary(pickle.dumps(global_assets)),)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Aggregation Successful: Global model updated in Central DB.")

if __name__ == "__main__":
    run_aggregation()