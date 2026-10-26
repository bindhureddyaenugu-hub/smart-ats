from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("upload/", views.upload_resumes, name="upload"),
path("process/", views.process_view, name="process"),
path("process/extract-text/", views.extract_text_step),
path("process/remove-bias/", views.remove_bias_step),
path("process/extract-skills/", views.extract_skills_step),
path("process/store/", views.store_step),

    path("rank/", views.rank_resumes, name="rank"),
    path("filter/", views.filter_by_skill, name="filter_skill"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path('delete-resume/<int:id>/', views.delete_resume, name='delete_resume'),
    path('clear-resumes/', views.clear_resumes, name='clear_resumes'),
    path('download-resume/<int:id>/', views.download_resume, name='download_resume'),
]
