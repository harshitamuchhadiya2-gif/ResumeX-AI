import PyPDF2
import re
import pandas as pd
import matplotlib.pyplot as plt
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills import skills_list

# Simple stopwords
STOP_WORDS = {
    "a", "an", "the", "and", "or", "is", "are", "to", "for", "of", "in",
    "on", "with", "as", "by", "at", "from", "that", "this", "it", "be"
}

# -------------------------------
# Extract text from PDF
# -------------------------------
def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    except:
        return ""
    return text.strip()

# -------------------------------
# Clean text
# -------------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    words = text.split()
    filtered_words = [word for word in words if word not in STOP_WORDS]
    return " ".join(filtered_words)

# -------------------------------
# Extract skills
# -------------------------------
def extract_skills(text):
    found_skills = set()
    text = text.lower()

    for skill in skills_list:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text):
            found_skills.add(skill)

    return sorted(list(found_skills))

# -------------------------------
# Calculate similarity
# -------------------------------
def calculate_similarity(resume_text, job_text):
    documents = [resume_text, job_text]
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
    return round(similarity[0][0] * 100, 2)

# -------------------------------
# Match level
# -------------------------------
def get_match_level(score):
    if score >= 80:
        return "🌟 Excellent Match"
    elif score >= 60:
        return "👍 Good Match"
    elif score >= 40:
        return "⚠️ Moderate Match"
    else:
        return "❌ Low Match"

# -------------------------------
# Suggestions
# -------------------------------
def generate_suggestions(missing_skills, score):
    suggestions = []

    if score < 60:
        suggestions.append("Add more job-relevant keywords to your resume.")
        suggestions.append("Tailor your resume specifically for this job role.")

    for skill in missing_skills:
        suggestions.append(f"Learn or add {skill} to improve your profile.")

    if not missing_skills and score >= 75:
        suggestions.append("Your resume is well aligned with the job role.")

    return suggestions

# -------------------------------
# Skill chart
# -------------------------------
def create_skill_chart(resume_skills, job_skills, missing_skills):
    data = {
        "Category": ["Resume Skills", "Job Skills", "Missing Skills"],
        "Count": [len(resume_skills), len(job_skills), len(missing_skills)]
    }
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df["Category"], df["Count"])
    ax.set_title("Skills Comparison")
    ax.set_ylabel("Count")

    chart_path = os.path.join("static", "skill_chart.png")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close(fig)

    return chart_path