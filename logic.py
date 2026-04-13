import PyPDF2
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from skills import skills_list

# -------------------------------
# Stop words
# -------------------------------
STOP_WORDS = {
    "the", "is", "in", "and", "to", "of", "a", "for", "on", "with",
    "as", "by", "an", "be", "this", "that", "it", "from", "or", "at"
}


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
    text = re.sub(r'[^a-zA-Z0-9\s\.\+\#]', ' ', text)
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
# Extract education
# -------------------------------
def extract_education(text):
    text = text.lower()

    education_map = {
        "bca": "BCA",
        "mca": "MCA",
        "b.tech": "B.Tech",
        "btech": "B.Tech",
        "m.tech": "M.Tech",
        "mtech": "M.Tech",
        "b.sc": "BSc",
        "bsc": "BSc",
        "m.sc": "MSc",
        "msc": "MSc",
        "b.com": "BCom",
        "bcom": "BCom",
        "m.com": "MCom",
        "mcom": "MCom",
        "bba": "BBA",
        "mba": "MBA",
        "ba": "BA",
        "ma": "MA",
        "diploma": "Diploma",
        "computer science": "Computer Science",
        "information technology": "Information Technology",
        "it": "IT",
        "engineering": "Engineering"
    }

    found_education = set()

    for keyword, display_name in education_map.items():
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, text):
            found_education.add(display_name)

    return sorted(list(found_education))


# -------------------------------
# Calculate similarity
# -------------------------------
# -------------------------------
# Professional ATS Match Score
# -------------------------------
def calculate_similarity(resume_text, job_text, resume_skills=None, job_skills=None):
    # ---------------------------
    # 1. Text similarity (25%)
    # ---------------------------
    documents = [resume_text, job_text]
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(documents)
    text_score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

    # ---------------------------
    # 2. Skill match score (50%)
    # ---------------------------
    skill_score = 0
    if resume_skills is not None and job_skills is not None and len(job_skills) > 0:
        matched = len(set(resume_skills) & set(job_skills))
        skill_score = (matched / len(job_skills)) * 100

    # ---------------------------
    # 3. Resume quality score (15%)
    # ---------------------------
    quality_score = 0
    word_count = len(resume_text.split())

    if word_count >= 250:
        quality_score += 40
    elif word_count >= 150:
        quality_score += 25
    else:
        quality_score += 10

    if len(resume_skills) >= 8:
        quality_score += 30
    elif len(resume_skills) >= 5:
        quality_score += 20
    else:
        quality_score += 10

    # Check for project/experience keywords
    quality_keywords = ["project", "experience", "internship", "certification", "developed", "implemented"]
    keyword_hits = sum(1 for kw in quality_keywords if kw in resume_text.lower())
    quality_score += min(keyword_hits * 5, 30)

    # Max cap
    quality_score = min(quality_score, 100)

    # ---------------------------
    # 4. Final weighted score
    # ---------------------------
    final_score = (
        (0.25 * text_score) +
        (0.50 * skill_score) +
        (0.25 * quality_score)
    )

    # ---------------------------
    # Professional score adjustment
    # ---------------------------
    # Prevent unrealistically low score if skills are somewhat matched
    if skill_score >= 40 and final_score < 50:
        final_score += 12

    if skill_score >= 60 and final_score < 65:
        final_score += 10

    if skill_score == 100 and final_score < 80:
        final_score = 82

    return round(min(final_score, 100), 2)


# -------------------------------
# Match level
# -------------------------------
# -------------------------------
# Match level
# -------------------------------
def get_match_level(score):
    if score >= 85:
        return "Excellent Match"
    elif score >= 70:
        return "Good Match"
    elif score >= 55:
        return "Moderate Match"
    elif score >= 40:
        return "Needs Improvement"
    else:
        return "Low Match"


# -------------------------------
# Application Recommendation
# -------------------------------
# -------------------------------
# Application Recommendation
# -------------------------------
# -------------------------------
# Application Recommendation
# -------------------------------
def get_application_advice(score):
    if score >= 85:
        return {
            "status": "Highly Recommended",
            "message": "Your resume is strongly aligned with this job role. You can confidently apply for this position.",
            "ats_readiness": "High",
            "highlight": "Your resume appears ATS-ready for this role."
        }
    elif score >= 50:
        return {
            "status": "Can Apply with Improvements",
            "message": "Your resume has a fair match with this job role. You can apply, but improving some missing skills and keywords will increase your chances.",
            "ats_readiness": "Moderate",
            "highlight": "Adding missing skills can significantly improve your chances."
        }
    else:
        return {
            "status": "Needs Significant Improvement",
            "message": "Your resume is not strongly aligned with this job role. It is better to improve your resume before applying.",
            "ats_readiness": "Low",
            "highlight": "You should improve your resume keywords, skills, and project descriptions before applying."
        }



# -------------------------------
# Suggestions
# -------------------------------
def generate_suggestions(missing_skills, score):
    suggestions = []

    if score < 60:
        suggestions.append("Add more job-relevant keywords to your resume.")
        suggestions.append("Tailor your resume specifically for this job role.")
        suggestions.append("Include measurable achievements and project outcomes.")

    for skill in missing_skills:
        suggestions.append(f"Consider adding or improving: {skill}")

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


# -------------------------------
# Suggest job roles (skills + education)
# -------------------------------
def suggest_job_roles(resume_skills, education_list=None):
    if education_list is None:
        education_list = []

    recommended = set()

    skill_map = {
        "python": ["Python Developer", "Backend Developer", "Software Developer"],
        "flask": ["Flask Developer", "Backend Developer", "Web Developer"],
        "django": ["Django Developer", "Backend Developer"],
        "machine learning": ["Machine Learning Engineer", "AI Engineer", "Data Scientist"],
        "data analysis": ["Data Analyst", "Business Analyst"],
        "sql": ["SQL Developer", "Database Developer", "Data Analyst"],
        "html": ["Frontend Developer", "Web Designer"],
        "css": ["UI Developer", "Frontend Developer"],
        "javascript": ["Frontend Developer", "Web Developer"],
        "react": ["React Developer", "Frontend Developer"],
        "java": ["Java Developer", "Software Engineer"],
        "c++": ["Software Developer", "Programmer Analyst"],
        "excel": ["Data Analyst", "MIS Executive", "Data Entry Executive"],
        "communication": ["Business Analyst", "HR Executive", "Customer Support Executive"],
        "tally": ["Accountant", "Finance Executive"],
        "power bi": ["BI Developer", "Data Analyst"]
    }

    education_map = {
        "BCA": ["Junior Software Developer", "Web Developer", "IT Support Executive", "QA Tester"],
        "MCA": ["Software Engineer", "Backend Developer", "Application Developer"],
        "B.Tech": ["Software Engineer", "System Engineer", "Developer"],
        "BSc": ["Data Analyst", "Lab Analyst", "IT Support"],
        "BBA": ["Business Analyst", "Sales Executive", "HR Executive"],
        "MBA": ["Project Manager", "Business Analyst", "Operations Executive"],
        "BCom": ["Accountant", "MIS Executive", "Finance Analyst"]
    }

    # Suggest based on skills
    for skill in resume_skills:
        skill_lower = skill.lower()
        if skill_lower in skill_map:
            for role in skill_map[skill_lower]:
                recommended.add(role)

    # Suggest based on education
    for edu in education_list:
        if edu in education_map:
            for role in education_map[edu]:
                recommended.add(role)

    if not recommended:
        recommended.update([
            "Junior IT Executive",
            "Software Trainee",
            "Technical Support Executive"
        ])

    return sorted(list(recommended))


# -------------------------------
# Resume feedback
# -------------------------------
def generate_resume_feedback(resume_skills, job_skills, missing_skills, match_score):
    feedback = []

    if match_score < 50:
        feedback.append("Your resume has a low match with this job. Consider tailoring it specifically for this role.")
    elif match_score < 75:
        feedback.append("Your resume has a moderate match. A few targeted improvements can significantly increase your chances.")
    else:
        feedback.append("Your resume has a strong match with this role. Minor optimization can make it even better.")

    if missing_skills:
        feedback.append(f"Add these important missing skills if you have them: {', '.join(missing_skills[:8])}.")
    else:
        feedback.append("Great! Your resume already includes most of the important skills from the job description.")

    if len(resume_skills) < 5:
        feedback.append("Your resume appears to list very few skills. Add more technical and professional skills relevant to your field.")

    feedback.append("Use strong action verbs like 'developed', 'built', 'implemented', and 'optimized' in your project descriptions.")
    feedback.append("Include measurable achievements such as percentages, project impact, or performance improvements.")
    feedback.append("Make sure your resume includes relevant projects, certifications, internships, and tools.")

    return feedback
