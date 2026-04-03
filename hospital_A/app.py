from fastapi import FastAPI, Body
import psycopg2
import pickle
import pandas as pd
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

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

# GLOBAL MODEL VARIABLES
artifacts = None
model = None
encoders = None
feature_names = None


# LOAD MODEL SAFELY
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


# SAFE DB CONNECTION
def get_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT"),
            sslmode="require"
        )
    except Exception as e:
        print("DB connection error:", e)
        return None


# HEALTH CHECK
@app.get("/")
def health():
    return {"status": "API running"}


# ADD PATIENT
@app.post("/add_patient")
def add_patient(data: dict = Body(...)):

    conn = get_connection()
    if conn is None:
        return {"error": "Database not connected"}

    try:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_records (
            id SERIAL PRIMARY KEY,
            age INT,
            bp INT,
            sg FLOAT,
            al INT,
            su INT,
            rbc TEXT,
            pc TEXT,
            pcc TEXT,
            ba TEXT,
            bgr FLOAT,
            bu FLOAT,
            sc FLOAT,
            sod FLOAT,
            pot FLOAT,
            hemo FLOAT,
            pcv FLOAT,
            wc FLOAT,
            rc FLOAT,
            htn TEXT,
            dm TEXT,
            cad TEXT,
            appet TEXT,
            pe TEXT,
            ane TEXT,
            classification TEXT
        )
        """)

        query = """
            INSERT INTO patient_records (
                age, bp, sg, al, su, rbc, pc, pcc, ba,
                bgr, bu, sc, sod, pot, hemo, pcv, wc, rc,
                htn, dm, cad, appet, pe, ane, classification
            )
            VALUES (
                %(age)s, %(bp)s, %(sg)s, %(al)s, %(su)s, %(rbc)s, %(pc)s, %(pcc)s, %(ba)s,
                %(bgr)s, %(bu)s, %(sc)s, %(sod)s, %(pot)s, %(hemo)s, %(pcv)s, %(wc)s, %(rc)s,
                %(htn)s, %(dm)s, %(cad)s, %(appet)s, %(pe)s, %(ane)s, %(classification)s
            )
        """

        cursor.execute(query, data)
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "patient record added successfully"}

    except Exception as e:
        return {
            "error": "Failed to add patient",
            "details": str(e)
        }


# LOCAL TRAINING
@app.post("/train_local")
def train_local():

    if not load_model():
        return {"error": "Model not loaded"}

    conn = get_connection()
    if conn is None:
        return {"error": "Database not connected"}

    try:
        df = pd.read_sql("SELECT * FROM patient_records", conn)

        if len(df) < 5:
            return {"message": "Not enough data to train"}

        # Drop unnecessary columns
        df = df.drop(columns=["id", "created_at"], errors="ignore")

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
            'cad','appet','pe','ane','classification'
        ]

        for col in categorical_cols:
            df[col] = encoders[col].transform(df[col].astype(str))

        # Split
        X = df.drop(columns=["classification"])
        y = df["classification"]

        # Maintain column order
        X = X[feature_names]

        # Train
        model.fit(X, y)

        # Save updated model
        updated_artifacts = {
            "model": model,
            "encoders": encoders,
            "feature_names": feature_names
        }

        save_path = os.path.join(BASE_DIR, "hospitalA_model.pkl")

        with open(save_path, "wb") as f:
            pickle.dump(updated_artifacts, f)

        conn.close()

        return {
            "status": "Local training complete",
            "records_used": len(df),
            "model_saved": "hospitalA_model.pkl"
        }

    except Exception as e:
        return {
            "error": "Training failed",
            "details": str(e)
        }