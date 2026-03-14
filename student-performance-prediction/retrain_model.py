# retrain_model.py

from pymongo import MongoClient
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import os


def retrain_model():

    try:
        # ================= MONGODB CONNECTION =================
        client = MongoClient(
            "mongodb+srv://USERNAME:PASSWORD@cluster0.mongodb.net/?retryWrites=true&w=majority"
        )

        db = client["student_prediction"]
        collection = db["students"]

        data = list(collection.find({}, {
            "_id": 0,
            "course": 1,
            "avg_marks": 1,
            "study_hours": 1,
            "predicted_score": 1
        }))

        if len(data) < 5:
            print("❌ Not enough data to retrain")
            return

        # ================= DATAFRAME =================
        df = pd.DataFrame(data)

        df.rename(columns={
            "predicted_score": "final_score"
        }, inplace=True)

        # ================= FEATURE ENGINEERING =================
        encoder = LabelEncoder()
        df["course_encoded"] = encoder.fit_transform(df["course"])

        X = df[["course_encoded", "avg_marks", "study_hours"]]
        y = df["final_score"]

        # ================= TRAIN MODEL =================
        model = LinearRegression()
        model.fit(X, y)

        # ================= SAVE MODEL =================
        os.makedirs("models", exist_ok=True)

        joblib.dump(model, "models/model.pkl")
        joblib.dump(encoder, "models/encoder.pkl")

        print("✅ Model retrained successfully")

    except Exception as e:
        print("❌ Retrain error:", e)
