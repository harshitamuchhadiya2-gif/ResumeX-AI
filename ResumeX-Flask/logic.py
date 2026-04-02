import PyPDF2
import nltk
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from skills import skills_list

# Download stopwords once
nltk.download('stopwords')
STOP_WORDS = set(stopwords.words('english'))


# -------------------------------
# Extract text from PDF
# -------------------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
        return text.strip(), None
    except Exception as e:
        return "", str(e)


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
# Chart data for frontend
# -------------------------------
def create_skill_chart_data(resume_skills, job_skills, missing_skills):
    return {
        "labels": ["Resume Skills", "Job Skills", "Missing Skills"],
        "values": [len(resume_skills), len(job_skills), len(missing_skills)]
    }

