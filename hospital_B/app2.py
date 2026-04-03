from fastapi import FastAPI
import psycopg2
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
import pickle
import pandas as pd

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

# BASE DIR (important for Render)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# CENTRAL DB CONFIG
CENTRAL_DB_PARAMS = {
    "host": os.getenv("CENTRAL_DB_HOST"),
    "database": os.getenv("CENTRAL_DB_NAME"),
    "user": os.getenv("CENTRAL_DB_USER"),
    "password": os.getenv("CENTRAL_DB_PASSWORD"),
    "sslmode": "require"
}


HOSPITAL_ID = "hospitalB"  


# SAFE DB CONNECTION
def get_central_connection():
    try:
        return psycopg2.connect(**CENTRAL_DB_PARAMS)
    except Exception as e:
        print("Central DB connection error:", e)
        return None


# HEALTH CHECK
@app.get("/")
def health():
    return {"status": "Sync service running"}


# PUSH LOCAL MODEL → CENTRAL
@app.post("/push_to_central")
def push_to_central():
    try:
        model_path = os.path.join(BASE_DIR, f"{HOSPITAL_ID}_model.pkl")

        if not os.path.exists(model_path):
            return {"error": "Local model not found. Run /train_local first."}

        with open(model_path, "rb") as f:
            model_bytes = f.read()

        conn = get_central_connection()
        if conn is None:
            return {"error": "Central DB not connected"}

        cursor = conn.cursor()

        # Create table safely
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

    except Exception as e:
        return {
            "error": "Push failed",
            "details": str(e)
        }


# PULL GLOBAL MODEL ← CENTRAL
@app.get("/pull_from_central")
def pull_from_central():
    try:
        conn = get_central_connection()
        if conn is None:
            return {"error": "Central DB not connected"}

        cursor = conn.cursor()

        cursor.execute("""
            SELECT model_data 
            FROM aggregated 
            ORDER BY updated_at DESC 
            LIMIT 1
        """)

        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return {"error": "No aggregated model found"}

        save_path = os.path.join(BASE_DIR, "initial_model.pkl")

        with open(save_path, "wb") as f:
            f.write(row[0])

        cursor.close()
        conn.close()

        return {
            "status": "Global model pulled successfully",
            "message": "Ready for next training round"
        }

    except Exception as e:
        return {
            "error": "Pull failed",
            "details": str(e)
        }
    

# GLOBAL VARIABLES
artifacts = None
model = None
encoders = None
feature_names = None


def load_model():
    global artifacts, model, encoders, feature_names
    try:
        if artifacts is None:
            model_path = os.path.join(BASE_DIR, "initial_model.pkl")

            with open(model_path, "rb") as f:
                artifacts = pickle.load(f)

            model = artifacts["model"]
            encoders = artifacts["encoders"]
            feature_names = artifacts["feature_names"]

        return True
    except Exception as e:
        print("Model load error:", e)
        return False


# PREDICT ENDPOINT
@app.post("/predict")
def predict(data: dict = Body(...)):

    if not load_model():
        return {"error": "Model not loaded"}

    try:
        df = pd.DataFrame([data])

        # Numeric columns
        numeric_cols = [
            'age','bp','sg','al','su','bgr','bu','sc',
            'sod','pot','hemo','pcv','wc','rc'
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())

        # Categorical columns
        categorical_cols = [
            'rbc','pc','pcc','ba','htn','dm',
            'cad','appet','pe','ane'
        ]

        for col in categorical_cols:
            df[col] = encoders[col].transform(df[col].astype(str))

        # Ensure column order
        df = df[feature_names]

        # Predict
        prediction = model.predict(df)[0]

        # Optional: decode output if encoder used
        try:
            prediction = encoders["classification"].inverse_transform([prediction])[0]
        except:
            pass

        return {
            "prediction": prediction
        }

    except Exception as e:
        return {
            "error": "Prediction failed",
            "details": str(e)
        }