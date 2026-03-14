import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import os


def retrain_model():

    # ================= DATABASE CONNECTION =================

    conn = mysql.connector.connect(
        host="sql201.infinityfree.com",
        user="if0_41338440",
        password="copycat2026",
        database="if0_41338440_student_prediction"
    )

    # ================= LOAD DATA =================

    query = """
    SELECT course, avg_marks, study_hours, final_score
    FROM students
    """

    df = pd.read_sql(query, conn)
    conn.close()

    print("Training Data Loaded:")
    print(df)

    # ================= CHECK DATA =================

    if df.empty or len(df) < 5:
        print("❌ Not enough student data for training")
        return

    # ================= ENCODE COURSE =================

    encoder = LabelEncoder()

    df["course_encoded"] = encoder.fit_transform(df["course"])

    # ================= FEATURES & TARGET =================

    X = df[["course_encoded", "avg_marks", "study_hours"]]
    y = df["final_score"]

    # ================= TRAIN MODEL =================

    model = LinearRegression()

    model.fit(X, y)

    # ================= CREATE MODELS FOLDER =================

    os.makedirs("models", exist_ok=True)

    # ================= SAVE MODEL =================

     os.makedirs("models", exist_ok=True)
        joblib.dump(model, "models/model.pkl")
        joblib.dump(encoder, "models/encoder.pkl")

    print("\n✅ Model retrained successfully")
    print("✅ models/model.pkl saved")
    print("✅ models/encoder.pkl saved")

 except Exception as e:
        print("❌ Retrain error:", e)
