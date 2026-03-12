from flask import Flask, request, jsonify
from model import predict_performance

app = Flask(__name__)

@app.route("/")
def home():
    return "Student Prediction API Running"

@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    course = data.get("course")
    avg_marks = float(data.get("avg_marks"))
    study_hours = float(data.get("study_hours"))

    try:
        final_score = predict_performance(course, avg_marks, study_hours)
    except Exception as e:
        return jsonify({"error":str(e)})

    return jsonify({
        "prediction":round(final_score,2)
    })


if __name__ == "__main__":
    app.run()
