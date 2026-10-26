import re
from pdfminer.high_level import extract_text

# -------- PDF TEXT EXTRACTION --------
def extract_text_from_pdf(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        return ""

# -------- REMOVE BIAS / PII --------
def remove_bias(text):
    # remove email
    text = re.sub(r'\S+@\S+', ' ', text)
    # remove phone numbers
    text = re.sub(r'\+?\d[\d -]{8,12}\d', ' ', text)
    # remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# -------- SKILL EXTRACTION (BASIC) --------
SKILLS_DB = [
    # Programming Languages
    "python", "java", "c", "c++", "c#", "javascript",

    # Backend / Frameworks
    "django", "flask", "spring", "spring boot", "springboot",
    "jsp", "hibernate",

    # Databases
    "sql", "mysql", "postgresql", "oracle", "mongodb",

    # Web
    "html", "css", "bootstrap", "react", "angular",

    # AI / ML
    "machine learning", "deep learning", "nlp",

    # DevOps / Cloud
    "aws", "docker", "kubernetes", "git"
]


def extract_skills(text):
    text = text.lower()
    found_skills = []
    for skill in SKILLS_DB:
        if skill in text:
            found_skills.append(skill)
    return list(set(found_skills))


def skill_gap_analysis(jd_skills, resume_skills):
    jd_set = set(jd_skills)
    resume_set = set(resume_skills)

    missing = list(jd_set - resume_set)
    matched = list(jd_set & resume_set)

    return matched, missing


def extract_jd_skills(jd_text):
    jd_text = jd_text.lower()
    return [skill for skill in SKILLS_DB if skill in jd_text]


def resume_quality_feedback(text, skills):
    feedback = []

    if len(text.split()) < 150:
        feedback.append("Resume content is too short")

    if len(skills) < 5:
        feedback.append("Add more technical skills")

    if not any("project" in text.lower() for _ in [1]):
        feedback.append("Project details missing")

    if not feedback:
        feedback.append("Resume is ATS friendly")

    return feedback


def candidate_recommendation(ats_score, matched_skills, missing_skills):
    """
    Returns candidate recommendation based on ATS score
    and skill gap analysis.
    """

    missing_count = len(missing_skills)
    matched_count = len(matched_skills)

    if ats_score >= 80 and missing_count <= 1 and matched_count >= 3:
        return "Highly Recommended"

    elif ats_score >= 50 and missing_count <= 3:
        return "Recommended"

    elif ats_score >= 40:
        return "Average Match"

    else:
        return "Low Match"
