import joblib
import numpy as np

# ================= PREDICTION FUNCTION =================

def predict_performance(course, avg_marks, study_hours):

    # Load model and encoder
    model = joblib.load("models/model.pkl")
    encoder = joblib.load("models/encoder.pkl")

    try:
        # Encode course
        course_encoded = encoder.transform([course])[0]
    except Exception:
        raise ValueError("Course not found in trained model")

    # Create feature array
    features = np.array([[course_encoded, avg_marks, study_hours]])

    # Predict expected score
    prediction = model.predict(features)[0]

    return float(prediction)
