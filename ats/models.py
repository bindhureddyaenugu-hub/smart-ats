from django.db import models
from django.contrib.auth.models import User

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class JobDescription(models.Model):
    title = models.CharField(max_length=200)
    jd_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 🔥 Link to user
    job = models.ForeignKey(JobDescription, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to="resumes/")
    cleaned_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    ats_score = models.FloatField(null=True, blank=True)
    file = models.FileField(upload_to="resumes/")
    cleaned_text = models.TextField(blank=True)
    skills = models.TextField(default="[]")

    ats_score = models.FloatField(null=True, blank=True)
    sbert_score = models.FloatField(null=True, blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username
