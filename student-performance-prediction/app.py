import mysql.connector
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from model import predict_performance
import os

app = Flask(__name__)

# Allow requests from InfinityFree frontend
CORS(app)


# ================= DATABASE CONNECTION =================

def get_connection():
    
# ================= SEARCH COURSES =================

@app.route("/search_courses")
def search_courses():

    query = request.args.get("query", "")
    level = request.args.get("level", "")

    conn = get_connection()

    if conn is None:
        return jsonify([])

    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT course_name
    FROM courses
    JOIN academic_levels
    ON courses.level_id = academic_levels.id
    WHERE academic_levels.level_name=%s
    AND course_name LIKE %s
    """

    cursor.execute(sql, (level, f"%{query}%"))
    data = cursor.fetchall()

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

    cursor = conn.cursor(dictionary=True)

    sql = """
    SELECT subject_name
    FROM subjects
    JOIN courses
    ON subjects.course_id = courses.id
    WHERE courses.course_name=%s
    AND subject_name LIKE %s
    """

    cursor.execute(sql, (course, f"%{query}%"))
    data = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(data)


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

    # ================= COLLECT SUBJECT MARKS =================

    for key in request.form:

        if "subject_mark_" in key:

            mark = request.form.get(key)

            if mark:
                mark = float(mark)

                subject_marks.append(mark)

                index = key.split("_")[-1]
                subject_name = request.form.get(f"subject_name_{index}")

                if subject_name:
                    subjects[subject_name] = mark

    if len(subject_marks) < 3:
        return "Enter at least 3 subjects"


    # ================= CALCULATIONS =================

    avg_marks = int(sum(subject_marks) / len(subject_marks))
    max_marks = max(subject_marks)


    # ================= ML PREDICTION =================

    try:
        final_score = float(
            predict_performance(course, avg_marks, study_hours)
        )
    except Exception as e:
        return f"Prediction error: {str(e)}"

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


    # ================= SAVE STUDENT DATA =================

    try:

        conn = get_connection()

        if conn is not None:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO students (course, avg_marks, study_hours, final_score)
                VALUES (%s,%s,%s,%s)
                """,
                (course, avg_marks, study_hours, final_score)
            )

            conn.commit()

            cursor.close()
            conn.close()

    except mysql.connector.Error as err:
        print("Database Error:", err)


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


    # ================= RETURN RESULT PAGE =================

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
