import joblib
import numpy as np

# ================= LOAD MODEL =================

model = joblib.load("models/model.pkl")

# ================= LOAD ENCODER =================

encoder = joblib.load("models/encoder.pkl")


# ================= PREDICTION FUNCTION =================

def predict_performance(course, avg_marks, study_hours):

    # Encode course
    course_encoded = encoder.transform([course])[0]

    # Create feature array
    features = np.array([[course_encoded, avg_marks, study_hours]])

    # Predict expected score
    prediction = model.predict(features)[0]

    return prediction