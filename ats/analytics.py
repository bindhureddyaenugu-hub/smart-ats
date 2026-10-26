import json
from collections import Counter


def analytics_data(resumes):
    """
    Generate analytics for the logged-in user's resumes.
    'resumes' must be a queryset passed from the view:
        Resume.objects.filter(user=request.user)
    """

    # Safety check (prevents WSGIRequest error)
    if not hasattr(resumes, "count"):
        raise ValueError("analytics_data() expected a Resume queryset, got something else.")

    ats_scores = []
    all_skills = []
    resume_rows = []

    for r in resumes:
        # -------------------------
        # Collect ATS Scores
        # -------------------------
        if r.ats_score is not None:
            ats_scores.append(r.ats_score)

        # -------------------------
        # Load Skills Safely
        # -------------------------
        try:
            skills = json.loads(r.skills)
            if not isinstance(skills, list):
                skills = []
        except (json.JSONDecodeError, TypeError):
            skills = []

        all_skills.extend(skills)

        # -------------------------
        # Prepare Table Row
        # -------------------------
        resume_rows.append({
            "name": r.file.name.split("/")[-1] if r.file else "N/A",
            "ats_score": round(r.ats_score, 2) if r.ats_score else 0,
            "skills": ", ".join(skills) if skills else "No skills extracted"
        })

    # -------------------------
    # Skill Frequency
    # -------------------------
    skill_freq = Counter(all_skills)

    # -------------------------
    # Average ATS Score
    # -------------------------
    avg_ats = round(sum(ats_scores) / len(ats_scores), 2) if ats_scores else 0

    return {
        "total_resumes": resumes.count(),
        "avg_ats": avg_ats,
        "top_skills": skill_freq.most_common(10),
        "resume_rows": resume_rows
    }