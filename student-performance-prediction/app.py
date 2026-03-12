import numpy as np
from flask import Flask, request, jsonify
from model import predict_performance

app = Flask(__name__)

# ================= HOME =================

@app.route("/")
def home():
    return "Student Performance Prediction API Running"


# ================= PREDICT =================

@app.route("/predict", methods=["POST"])
def predict():

    # Receive JSON from predict.php
    data = request.get_json(force=True)

    level = data.get("level")
    course = data.get("course")
    study_hours = data.get("study_hours")

    if study_hours is None or study_hours == "":
        return jsonify({"error": "Study hours required"})

    study_hours = float(study_hours)

    subjects = {}
    subject_marks = []

    # Collect subject marks
    for key in data:

        if "subject_mark_" in key:

            mark = data.get(key)

            if mark and mark != "":

                mark = float(mark)
                subject_marks.append(mark)

                index = key.split("_")[-1]
                subject_name = data.get(f"subject_name_{index}")

                if subject_name:
                    subjects[subject_name] = mark

    if len(subject_marks) < 3:
        return jsonify({"error": "Enter at least 3 subjects"})


    # ================= CALCULATIONS =================

    avg_marks = sum(subject_marks) / len(subject_marks)


    # ================= ML PREDICTION =================

    try:
        final_score = predict_performance(course, avg_marks, study_hours)
    except Exception as e:
        return jsonify({"error": str(e)})


    expected_mark = round(final_score, 2)


    # ================= RESULT LABEL =================

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


    # ================= IMPROVEMENT PLAN =================

    improvement_plan = {}

    for subject, mark in subjects.items():

        if mark < 30:
            extra_hours = 2
            expected = "45+"
        elif mark < 45:
            extra_hours = 1.5
            expected = "50+"
        elif mark < 60:
            extra_hours = 1
            expected = "65+"
        else:
            extra_hours = 0.5
            expected = "70+"

        improvement_plan[subject] = {
            "mark": mark,
            "extra_hours": extra_hours,
            "expected": expected
        }


    # ================= WEEKLY TIMETABLE =================

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    weekly_timetable = {}

    weak = []
    medium = []
    strong = []

    for subject, mark in subjects.items():

        if mark < 45:
            weak.append(subject)
        elif mark < 60:
            medium.append(subject)
        else:
            strong.append(subject)

    for day in days:

        weekly_timetable[day] = []

        if day == "Saturday":
            weekly_timetable[day].append("All Subjects Revision")
            continue

        if day == "Sunday":
            weekly_timetable[day].append("Mock Test")
            continue

        for subject in weak:
            weekly_timetable[day].append(f"{subject} - 2 hrs")

        if day in ["Monday","Wednesday","Friday"]:
            for subject in medium:
                weekly_timetable[day].append(f"{subject} - 1.5 hrs")

        if day in ["Tuesday","Thursday"]:
            for subject in strong:
                weekly_timetable[day].append(f"{subject} - 1 hr")


    weakest_subject = min(subjects, key=subjects.get)


    # Return JSON instead of HTML
    return jsonify({

        "course": course,
        "final_score": round(final_score, 2),
        "expected_mark": expected_mark,
        "prediction": prediction,
        "weakest_subject": weakest_subject,
        "improvement_plan": improvement_plan,
        "weekly_timetable": weekly_timetable

    })


# ================= RUN =================

if __name__ == "__main__":
    app.run()
