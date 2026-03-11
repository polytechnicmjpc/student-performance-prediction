
import psycopg2
import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from model import predict_performance

app = Flask(__name__)

# Allow frontend requests
CORS(app)

# ================= DATABASE CONNECTION =================

def get_connection():
    try:
        DATABASE_URL = os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print("Database connection error:", e)
        return None


# ================= SEARCH COURSES =================

@app.route("/search_courses")
def search_courses():

    query = request.args.get("query", "")
    level = request.args.get("level", "")

    conn = get_connection()

    if conn is None:
        return jsonify([])

    cursor = conn.cursor()

    sql = """
    SELECT course_name
    FROM courses
    JOIN academic_levels
    ON courses.level_id = academic_levels.id
    WHERE academic_levels.level_name=%s
    AND course_name ILIKE %s
    """

    cursor.execute(sql, (level, f"%{query}%"))

    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({"course_name": row[0]})

    cursor.close()
    conn.close()

    return jsonify(data)


# ================= SEARCH SUBJECTS =================

@app.route("/search_subjects")
def search_subjects():

    query = request.args.get("query", "")
    course = request.args.get("course", "")

    conn = get_connection()

    if conn is None:
        return jsonify([])

    cursor = conn.cursor()

    sql = """
    SELECT subject_name
    FROM subjects
    JOIN courses
    ON subjects.course_id = courses.id
    WHERE courses.course_name=%s
    AND subject_name ILIKE %s
    """

    cursor.execute(sql, (course, f"%{query}%"))

    rows = cursor.fetchall()

    data = []
    for row in rows:
        data.append({"subject_name": row[0]})

    cursor.close()
    conn.close()

    return jsonify(data)


# ================= PREDICT RESULT =================

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

    # ===== Collect subject marks =====

    for key in request.form.keys():

        if key.startswith("subject_mark_"):

            index = key.split("_")[-1]

            mark = request.form.get(key)
            subject_name = request.form.get(f"subject_name_{index}")

            if mark and subject_name:

                mark = float(mark)

                subject_marks.append(mark)
                subjects[subject_name] = mark

    if len(subject_marks) < 3:
        return "Enter at least 3 subjects"

    # ===== Calculate average =====

    avg_marks = int(sum(subject_marks) / len(subject_marks))

    # ===== ML Prediction =====

    try:
        final_score = float(
            predict_performance(course, avg_marks, study_hours)
        )
    except Exception as e:
        return f"Prediction error: {str(e)}"

    expected_mark = round(final_score, 2)

    # ===== Performance Label =====

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

    # ================= WEEKLY STUDY PLAN =================

    days = [
        "Monday","Tuesday","Wednesday",
        "Thursday","Friday","Saturday","Sunday"
    ]

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

    # ================= SHOW RESULT PAGE =================

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


# ================= RUN APP =================

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=port)
