from django.shortcuts import render, redirect
from .forms import ResumeUploadForm
from .models import Resume
from .utils import extract_text_from_pdf, remove_bias, extract_skills
from .models import JobDescription, Resume
from .forms import JobDescriptionForm
from .sbert import get_embedding
from .ranking import calculate_ats_score
import pymysql


from django.contrib.auth.decorators import login_required

@login_required
def upload_resumes(request):
    if request.method == "POST":
        files = request.FILES.getlist("resumes")

        for f in files:
            Resume.objects.create(
                user=request.user,  # attach to logged user
                file=f,
                cleaned_text="",
                skills="[]"
            )

        return redirect("process")

    return render(request, "ats/process.html")


from .utils import extract_text_from_pdf

@login_required
def extract_text_step(request):
    resumes = Resume.objects.filter(user=request.user)

    for resume in resumes:
        if not resume.cleaned_text:
            text = extract_text_from_pdf(resume.file.path)
            resume.cleaned_text = text
            resume.save()

    return redirect("process")


from .utils import remove_bias

@login_required
def remove_bias_step(request):
    resumes = Resume.objects.filter(user=request.user)

    for resume in resumes:
        resume.cleaned_text = remove_bias(resume.cleaned_text)
        resume.save()

    return redirect("process")


import json
from .utils import extract_skills

@login_required
def extract_skills_step(request):
    resumes = Resume.objects.filter(user=request.user)

    for resume in resumes:
        skills = extract_skills(resume.cleaned_text)
        resume.skills = json.dumps(skills)
        resume.save()

    return redirect("process")


def store_step(request):
    request.session["step"] = 5
    return redirect("process")

@login_required
def process_view(request):
    count = Resume.objects.filter(user=request.user).count()
    return render(request, "ats/process.html", {"count": count})


from .utils import extract_jd_skills, skill_gap_analysis
import json
from .utils import resume_quality_feedback, candidate_recommendation

def rank_resumes(request):
    if request.method == "POST":
        form = JobDescriptionForm(request.POST)

        if form.is_valid():
            # -------------------------
            # 1️⃣ Get Job Description
            # -------------------------
            title = form.cleaned_data["title"]
            jd_text = form.cleaned_data["jd_text"]

            jd = JobDescription.objects.create(
                title=title,
                jd_text=jd_text
            )

            # -------------------------
            # 2️⃣ JD Embedding & Skills
            # -------------------------
            jd_vector = get_embedding(jd_text)
            jd_skills = extract_jd_skills(jd_text)

            resumes = Resume.objects.filter(user=request.user)
            results = []

            # -------------------------
            # 3️⃣ Process Each Resume
            # -------------------------
            for resume in resumes:
                # Skip empty resumes safely
                if not resume.cleaned_text:
                    continue

                # SBERT embedding
                resume_vector = get_embedding(resume.cleaned_text)

                # ATS score
                ats_score = calculate_ats_score(resume_vector, jd_vector)

                # Save score in DB (MySQL)
                resume.ats_score = ats_score
                resume.sbert_score = ats_score
                resume.save(update_fields=["ats_score", "sbert_score"])

                # -------------------------
                # 4️⃣ SAFE Skill Loading
                # -------------------------
                try:
                    resume_skills = json.loads(resume.skills)
                    if not isinstance(resume_skills, list):
                        resume_skills = []
                except (json.JSONDecodeError, TypeError):
                    resume_skills = []

                # -------------------------
                # 5️⃣ Skill Gap Analysis
                # -------------------------
                matched, missing = skill_gap_analysis(jd_skills, resume_skills)

                # UX-friendly missing skills
                if not missing:
                    missing_display = ["No missing skills"]
                else:
                    missing_display = missing
                # -------------------------
                # 6️⃣ Resume Quality Feedback
                # -------------------------
                feedback = resume_quality_feedback(
                    resume.cleaned_text, resume_skills
                )

                # -------------------------
                # 7️⃣ Recommendation Logic
                # -------------------------
                recommendation = candidate_recommendation(
                    ats_score,
                    matched,
                    missing
                )

                # -------------------------
                # 8️⃣ Collect Results
                # -------------------------
                results.append({
                    "resume": resume,
                    "matched": matched,
                    "missing": missing_display,
                    "feedback": feedback,
                    "recommendation": recommendation
                })

            # -------------------------
            # 9️⃣ Sort by ATS Score
            # -------------------------
            results.sort(
                key=lambda x: x["resume"].ats_score,
                reverse=True
            )

            return render(
                request,
                "ats/rank.html",
                {
                    "results": results,
                    "jd": jd,
                    "jd_skills": jd_skills
                }
            )

    # -------------------------
    # GET Request
    # -------------------------
    else:
        form = JobDescriptionForm()

    return render(request, "ats/jd_upload.html", {"form": form})

@login_required
def filter_by_skill(request):
    skill = request.GET.get("skill", "").strip().lower()
    resumes = Resume.objects.filter(user=request.user)
    filtered_resumes = []

    for resume in resumes:
        try:
            skills = json.loads(resume.skills)
            if skill in skills:
                filtered_resumes.append(resume)
        except:
            pass

    return render(request, "ats/filter.html", {
        "skill": skill,
        "resumes": filtered_resumes
    })


from .models import Resume
from .analytics import analytics_data
from django.contrib.auth.decorators import login_required

@login_required
def analytics_dashboard(request):
    # Get resumes of the logged-in user ONLY
    resumes = Resume.objects.filter(user=request.user)

    # Send queryset to analytics engine
    data = analytics_data(resumes)

    return render(request, "ats/analytics.html", data)


from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm

# ---------- Landing Page ----------
def landing(request):
    return render(request, "ats/landing.html")


# ---------- Registration ----------
from .models import Profile

from .models import Profile

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ✅ Create profile ONLY if it doesn't exist
            profile, created = Profile.objects.get_or_create(user=user)

            # ✅ Update values safely
            profile.mobile = form.cleaned_data["mobile"]
            profile.address = form.cleaned_data["address"]
            profile.save()

            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "ats/register.html", {"form": form})


# ---------- Login ----------
def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Invalid credentials"

    return render(request, "ats/login.html", {"error": error})


# ---------- Logout ----------
def logout_view(request):
    logout(request)
    return redirect("landing")


@login_required
def dashboard(request):
    return render(request, "ats/dashboard.html")


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Resume

@login_required
def delete_resume(request, id):

    resume = get_object_or_404(
        Resume,
        id=id
    )

    # Delete Resume
    resume.delete()

    return redirect("analytics")


@login_required
def clear_resumes(request):

    Resume.objects.filter(user=request.user).delete()

    return redirect('rank')

from django.http import FileResponse

@login_required
def download_resume(request, id):

    resume = get_object_or_404(
        Resume,
        id=id,
        user=request.user
    )

    return FileResponse(
        resume.file.open('rb'),
        as_attachment=True,
        filename=resume.file.name.split("/")[-1]
    )