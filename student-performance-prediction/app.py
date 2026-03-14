from flask import Flask, render_template, request
from flask_cors import CORS
from pymongo import MongoClient
from model import predict_performance
from retrain_model import retrain_model
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ================= MONGODB CONNECTION =================
client = MongoClient("mongodb+srv://studentadmin:copycat2026@cluster0.eu4t0uq.mongodb.net/?appName=Cluster0")
db = client["student_prediction"]
students_collection = db["students"]

# ================= HOME =================
@app.route("/")
def home():
    return render_template("home.html")


# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():

    level = request.form.get("level")
    course = request.form.get("course")
    study_hours = request.form.get("study_hours")

    if not study_hours:
        return "Study hours required"

    study_hours = float(study_hours)

    subjects = {}
    subject_marks = []

    i = 0
    while True:

        subject_name = request.form.get(f"subject_name_{i}")
        series1 = request.form.get(f"series1_mark_{i}")
        series2 = request.form.get(f"series2_mark_{i}")

        if not subject_name:
            break

        if series1 and series2:
            series1 = float(series1)
            series2 = float(series2)

            avg_mark = (series1 + series2) / 2
            subjects[subject_name] = avg_mark
            subject_marks.append(avg_mark)

        i += 1

    if len(subject_marks) < 3:
        return "Enter at least 3 subjects"

    avg_marks = int(sum(subject_marks) / len(subject_marks))

    # ================= MODEL PREDICTION =================
    try:
        final_score = float(
            predict_performance(course, avg_marks, study_hours)
        )
    except Exception as e:
        return f"Prediction error: {str(e)}"

    expected_mark = round(final_score, 2)

    if final_score >= 65:
        prediction = "Excellent 🏆"
    elif final_score >= 55:
        prediction = "Very Good 🌟"
    elif final_score >= 45:
        prediction = "Good 👍"
    elif final_score >= 35:
        prediction = "Average 🙂"
    else:
        prediction = "Needs Improvement ⚠️"

    # ================= SAVE STUDENT DATA (MongoDB) =================
    try:

        student_data = {
            "level": level,
            "course": course,
            "subjects": subjects,
            "avg_marks": avg_marks,
            "study_hours": study_hours,
            "predicted_score": final_score,
            "created_at": datetime.utcnow()
        }

        students_collection.insert_one(student_data)

        # Retrain model automatically
        try:
            retrain_model()
        except Exception as e:
            print("Retrain error:", e)

    except Exception as e:
        print("MongoDB Insert Error:", e)

    # ================= IMPROVEMENT PLAN =================
    improvement_plan = {}

    for subject, mark in subjects.items():

        if mark < 10:
            extra_hours = 2
            expected = "45+ / 75"

        elif mark < 20:
            extra_hours = 1.5
            expected = "55+ / 75"

        elif mark < 30:
            extra_hours = 1
            expected = "65+ / 75"

        else:
            extra_hours = 0.5
            expected = "70+ / 75"

        improvement_plan[subject] = {
            "mark": f"{int(mark)} / 40",
            "extra_hours": extra_hours,
            "expected": expected
        }

    # ================= WEEKLY TIMETABLE =================
    days = [
        "Monday","Tuesday","Wednesday",
        "Thursday","Friday","Saturday","Sunday"
    ]

    weak = []
    medium = []
    strong = []

    for subject, mark in subjects.items():

        if mark < 15:
            weak.append(subject)

        elif mark < 25:
            medium.append(subject)

        else:
            strong.append(subject)

    weekly_timetable = {}

    for day in days:

        weekly_timetable[day] = []

        if day == "Saturday":
            weekly_timetable[day].append("All Subjects Revision")
            continue

        if day == "Sunday":
            weekly_timetable[day].append("Mock Test")
            continue

        for subject in weak:
            weekly_timetable[day].append(
                f"{subject} - {improvement_plan[subject]['extra_hours']} hrs/day"
            )

        if day in ["Monday","Wednesday","Friday"]:
            for subject in medium:
                weekly_timetable[day].append(
                    f"{subject} - {improvement_plan[subject]['extra_hours']} hrs/day"
                )

        if day in ["Tuesday","Thursday"]:
            for subject in strong:
                weekly_timetable[day].append(
                    f"{subject} - {improvement_plan[subject]['extra_hours']} hrs/day"
                )

    weakest_subject = min(subjects, key=subjects.get)

    # ================= RESULT PAGE =================
    return render_template(
        "result.html",
        level=level,
        course=course,
        final_score=round(final_score,2),
        expected_mark=expected_mark,
        prediction=prediction,
        improvement_plan=improvement_plan,
        weekly_timetable=weekly_timetable,
        weakest_subject=weakest_subject
    )


# ================= MANUAL RETRAIN =================
@app.route("/retrain")
def retrain():
    try:
        retrain_model()
        return "Model retrained successfully ✅"
    except Exception as e:
        return f"Retrain failed: {str(e)}"


# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=True)
