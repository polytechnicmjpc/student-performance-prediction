import json
from flask import Flask, request, jsonify
from model import predict_performance
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from your frontend

# ================= PREDICT PERFORMANCE =================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()  # Expect JSON from frontend

    level = data.get("level")
    course = data.get("course")
    study_hours = float(data.get("study_hours", 0))

    subjects_data = data.get("subjects", [])  # Expect: [{"name": "Math", "series1": 30, "series2": 28}, ...]

    if len(subjects_data) < 3:
        return jsonify({"error": "Enter at least 3 subjects"}), 400

    subjects = {}
    subject_marks = []

    for sub in subjects_data:
        name = sub["name"]
        series1 = float(sub["series1"])
        series2 = float(sub["series2"])
        avg_mark = (series1 + series2) / 2
        subjects[name] = avg_mark
        subject_marks.append(avg_mark)

    avg_marks = sum(subject_marks) / len(subject_marks)

    try:
        final_score = float(predict_performance(course, avg_marks, study_hours))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weak, medium, strong = [], [], []

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
            weekly_timetable[day].append(f"{subject} - {improvement_plan[subject]['extra_hours']} hrs/day")
        if day in ["Monday", "Wednesday", "Friday"]:
            for subject in medium:
                weekly_timetable[day].append(f"{subject} - {improvement_plan[subject]['extra_hours']} hrs/day")
        if day in ["Tuesday", "Thursday"]:
            for subject in strong:
                weekly_timetable[day].append(f"{subject} - {improvement_plan[subject]['extra_hours']} hrs/day")

    weakest_subject = min(subjects, key=subjects.get)

    return jsonify({
        "course": course,
        "final_score": round(final_score, 2),
        "prediction": prediction,
        "improvement_plan": improvement_plan,
        "weekly_timetable": weekly_timetable,
        "weakest_subject": weakest_subject
    })


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
