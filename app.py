from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, send_file
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash


from logic import (
    extract_text_from_pdf,
    clean_text,
    extract_skills,
    extract_education,
    calculate_similarity,
    get_match_level,
    generate_suggestions,
    create_skill_chart_data,
    suggest_job_roles,
    generate_resume_feedback,
    get_application_advice
)

app = Flask(__name__)
app.secret_key = "resumex_secret_key"

UPLOAD_FOLDER = "uploads"
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# -------------------------------
# Helpers
# -------------------------------
def load_json_file(filename, default_value):
    if not os.path.exists(filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(default_value, f, indent=4)

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_value


def save_json_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def load_users():
    return load_json_file(USERS_FILE, [])


def save_users(users):
    save_json_file(USERS_FILE, users)


def load_history():
    return load_json_file(HISTORY_FILE, [])


def save_history(history):
    save_json_file(HISTORY_FILE, history)


# -------------------------------
# Routes
# -------------------------------

# Landing Page
@app.route("/")
def home():
    if session.get("logged_in"):
        return redirect(url_for("analyzer_page"))
    return render_template("landing.html")


# Register Page
@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("logged_in"):
        return redirect(url_for("analyzer_page"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        users = load_users()

        for user in users:
            if user.get("email") == email:
                flash("Email already registered. Please login.", "warning")
                return redirect(url_for("login"))

        hashed_password = generate_password_hash(password)

        users.append({
    "name": name,
    "email": email,
    "password": hashed_password
})

        save_users(users)

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("analyzer_page"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        users = load_users()

        for user in users:
            if user.get("email") == email and check_password_hash(user.get("password"), password):
                session["logged_in"] = True
                session["user_name"] = user.get("name", "User")
                session["user_email"] = user.get("email")
                flash(f"Welcome back, {user.get('name', 'User')}!", "success")
                return redirect(url_for("analyzer_page"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


# Analyzer Page
@app.route("/analyzer")
def analyzer_page():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("index.html")


# About Page
@app.route("/about")
def about():
    return render_template("about.html")


# History Page
@app.route("/history")
def history_page():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    user_email = session.get("user_email")
    history = load_history()

    user_history = [item for item in history if item.get("email") == user_email]
    user_history = sorted(user_history, key=lambda x: x.get("timestamp", ""), reverse=True)

    return render_template("history.html", history=user_history)


# Analyze Resume
@app.route("/analyze", methods=["POST"])
def analyze():
    if not session.get("logged_in"):
        return jsonify({"error": "Please login first."}), 401

    try:
        if "resume" not in request.files:
            return jsonify({"error": "Resume file is required."}), 400

        resume_file = request.files["resume"]
        job_description = request.form.get("job_description", "").strip()

        if resume_file.filename == "":
            return jsonify({"error": "Please upload a resume."}), 400

        if not job_description:
            return jsonify({"error": "Please enter a job description."}), 400

        filename = secure_filename(resume_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        resume_file.save(file_path)

        resume_text, error = extract_text_from_pdf(file_path)

        if error:
            return jsonify({"error": error}), 400

        if not resume_text:
            return jsonify({"error": "Could not extract text from PDF."}), 400

        # Clean text
        cleaned_resume = clean_text(resume_text)
        cleaned_job = clean_text(job_description)

        # Extract data
        resume_skills = extract_skills(cleaned_resume)
        job_skills = extract_skills(cleaned_job)
        education_list = extract_education(resume_text)

        # Missing skills
        missing_skills = sorted(list(set(job_skills) - set(resume_skills)))

        # Score and advice
        match_score = float(calculate_similarity(cleaned_resume, cleaned_job, resume_skills, job_skills))
        match_level = get_match_level(match_score)
        application_advice = get_application_advice(match_score)

        # Suggestions and recommendations
        suggestions = generate_suggestions(missing_skills, match_score)
        recommended_jobs = suggest_job_roles(resume_skills, education_list)
        ai_feedback = generate_resume_feedback(resume_skills, job_skills, missing_skills, match_score)

        # Stats
        resume_word_count = len(cleaned_resume.split())
        job_word_count = len(cleaned_job.split())
        keyword_overlap = len(set(resume_skills) & set(job_skills))

        # Chart
        chart_data = create_skill_chart_data(resume_skills, job_skills, missing_skills)

        # Final result
        result_data = {
            "id": uuid.uuid4().hex,
            "email": session.get("user_email"),
            "name": session.get("user_name", "User"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "match_score": round(match_score, 2),
            "match_level": match_level,
            "application_status": application_advice["status"],
            "application_message": application_advice["message"],
            "education_list": education_list,
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "recommended_jobs": recommended_jobs,
            "ai_feedback": ai_feedback,
            "resume_word_count": resume_word_count,
            "job_word_count": job_word_count,
            "keyword_overlap": keyword_overlap,
            "chart_data": chart_data
        }

        # Save history
        history = load_history()
        history.append(result_data)
        save_history(history)

        return jsonify(result_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Download Report
@app.route("/download-report/<report_id>")
def download_report(report_id):
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    history = load_history()
    user_email = session.get("user_email")

    user_reports = [item for item in history if item.get("email") == user_email]

    report = None

    # Find by unique ID
    for item in user_reports:
        if item.get("id") == report_id:
            report = item
            break

    # Fallback: old index-based reports
    if not report and report_id.isdigit():
        report_index = int(report_id)
        if 0 <= report_index < len(user_reports):
            report = user_reports[report_index]

    if not report:
        flash("Report not found.", "danger")
        return redirect(url_for("history_page"))

    report_text = f"""
ResumeX Pro - Resume Analysis Report
====================================

Name: {report.get('name', 'User')}
Email: {report.get('email', 'N/A')}
Date: {report.get('timestamp', 'N/A')}
Resume File: {report.get('filename', 'N/A')}

Match Score: {report.get('match_score', 0)}%
Match Level: {report.get('match_level', 'N/A')}

Application Recommendation:
Status: {report.get('application_status', 'N/A')}
Message: {report.get('application_message', 'N/A')}

Detected Education:
{', '.join(report.get('education_list', []))}

Resume Skills:
{', '.join(report.get('resume_skills', []))}

Job Skills:
{', '.join(report.get('job_skills', []))}

Missing Skills:
{', '.join(report.get('missing_skills', []))}

Suggestions:
- """ + "\n- ".join(report.get('suggestions', [])) + """

Recommended Jobs:
- """ + "\n- ".join(report.get('recommended_jobs', [])) + """

AI Resume Feedback:
- """ + "\n- ".join(report.get('ai_feedback', []))

    buffer = BytesIO()
    buffer.write(report_text.encode("utf-8"))
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="resume_analysis_report.txt",
        mimetype="text/plain"
    )


if __name__ == "__main__":
    app.run(debug=True)