from sklearn.metrics.pairwise import cosine_similarity

def calculate_ats_score(resume_vector, jd_vector):
    score = cosine_similarity(
        [resume_vector], [jd_vector]
    )[0][0]
    return round(score * 100, 2)
