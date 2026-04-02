from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import os
import json
from datetime import datetime

from logic import (
    extract_text_from_pdf,
    clean_text,
    extract_skills,
    calculate_similarity,
    get_match_level,
    generate_suggestions,
    create_skill_chart_data
)

app = Flask(__name__)
app.secret_key = "resumex_secret_key"

UPLOAD_FOLDER = "uploads"
USERS_FILE = "users.json"
HISTORY_FILE = "history.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ----------------------------
# Helper Functions
# ----------------------------
def load_json(file_name):
    if not os.path.exists(file_name):
        with open(file_name, "w") as f:
            json.dump([], f)
    with open(file_name, "r") as f:
        return json.load(f)


def save_json(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        users = load_json(USERS_FILE)

        for user in users:
            if user.get("email") == email:
                flash("Email already registered. Please login.", "warning")
                return redirect(url_for("login"))

        users.append({
            "username": username,
            "email": email,
            "password": password
        })

        save_json(USERS_FILE, users)
        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        users = load_json(USERS_FILE)

        for user in users:
            if user.get("email") == email and user.get("password") == password:
                session["logged_in"] = True
                session["email"] = user.get("email")
                session["username"] = user.get("username", "User")
                flash("Login successful!", "success")
                return redirect(url_for("analyzer_page"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


@app.route("/analyzer")
def analyzer_page():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))
    return render_template("analyzer.html")


@app.route("/history")
def history():
    if not session.get("logged_in"):
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    all_history = load_json(HISTORY_FILE)
    user_email = session.get("email")

    user_history = [item for item in all_history if item.get("email") == user_email]
    user_history.reverse()

    return render_template("history.html", history=user_history)


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

        file_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(file_path)

        resume_text, error = extract_text_from_pdf(file_path)

        if error:
            return jsonify({"error": error}), 400

        if not resume_text:
            return jsonify({"error": "Could not extract text from PDF."}), 400

        cleaned_resume = clean_text(resume_text)
        cleaned_job = clean_text(job_description)

        match_score = float(calculate_similarity(cleaned_resume, cleaned_job))
        match_level = get_match_level(match_score)

        resume_skills = extract_skills(cleaned_resume)
        job_skills = extract_skills(cleaned_job)
        missing_skills = sorted(list(set(job_skills) - set(resume_skills)))

        suggestions = generate_suggestions(missing_skills, match_score)

        resume_word_count = len(cleaned_resume.split())
        job_word_count = len(cleaned_job.split())
        keyword_overlap = len(set(resume_skills) & set(job_skills))

        chart_data = create_skill_chart_data(resume_skills, job_skills, missing_skills)

        result = {
            "match_score": round(match_score, 2),
            "match_level": match_level,
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "resume_word_count": resume_word_count,
            "job_word_count": job_word_count,
            "keyword_overlap": keyword_overlap,
            "chart_data": chart_data
        }

        # Save history
        all_history = load_json(HISTORY_FILE)
        all_history.append({
            "email": session.get("email"),
            "username": session.get("username"),
            "resume_name": resume_file.filename,
            "match_score": result["match_score"],
            "match_level": result["match_level"],
            "missing_skills": result["missing_skills"],
            "date": datetime.now().strftime("%d-%m-%Y %I:%M %p")
        })
        save_json(HISTORY_FILE, all_history)

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
