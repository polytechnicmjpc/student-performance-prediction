# retrain_model.py

import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import os

def retrain_model():
    try:
        conn =  mysql.connector.connect(
        host="sql201.infinityfree.com",
        user="if0_41338440",
        password="copycat2026",
        database="if0_41338440_student_prediction"
    )
        df = pd.read_sql("SELECT course, avg_marks, study_hours, final_score FROM students", conn)
        conn.close()

        if df.empty or len(df) < 5:
            print("❌ Not enough data to retrain")
            return

        encoder = LabelEncoder()
        df["course_encoded"] = encoder.fit_transform(df["course"])
        X = df[["course_encoded", "avg_marks", "study_hours"]]
        y = df["final_score"]

        model = LinearRegression()
        model.fit(X, y)

        os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")
        joblib.dump(encoder, "models/encoder.pkl")
        print("✅ Model retrained successfully")
    except Exception as e:
        print("❌ Retrain error:", e)
