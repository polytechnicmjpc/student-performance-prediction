import mysql.connector
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import joblib
import os


# ================= DATABASE CONNECTION =================

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="student_prediction"
)


# ================= LOAD DATA FROM DATABASE =================

query = """
SELECT course, avg_marks, study_hours, final_score
FROM students
"""

df = pd.read_sql(query, conn)

conn.close()

print("Training Data Loaded:")
print(df)


# ================= CHECK DATA =================

if df.empty:
    print("❌ No student data found in database")
    exit()


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

joblib.dump(model, "models/model.pkl")

joblib.dump(encoder, "models/encoder.pkl")


print("\n✅ Model trained successfully")
print("✅ models/model.pkl saved")
print("✅ models/encoder.pkl saved")