from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)

    level = data.get("level")
    course = data.get("course")
    study_hours = data.get("study_hours")

    if study_hours is None or study_hours == "":
        return "Study hours required", 400

    study_hours = float(study_hours)

    subjects = {}
    subject_marks = []

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
        return "Enter at least 3 subjects", 400

    avg_marks = sum(subject_marks) / len(subject_marks)

    # Your model prediction function (make sure this works)
    final_score = predict_performance(course, avg_marks, study_hours)

    expected_mark = round(final_score, 2)

    # Prediction label logic
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

    # Build improvement_plan, weekly_timetable, weakest_subject exactly as before
    # ...

    return render_template(
        "result.html",
        course=course,
        final_score=round(final_score, 2),
        expected_mark=expected_mark,
        prediction=prediction,
        improvement_plan=improvement_plan,
        weekly_timetable=weekly_timetable,
        weakest_subject=weakest_subject
    )
