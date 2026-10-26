from django import forms

class ResumeUploadForm(forms.Form):
    resumes = forms.FileField(required=True)


class JobDescriptionForm(forms.Form):
    title = forms.CharField(max_length=200)
    jd_text = forms.CharField(widget=forms.Textarea(attrs={"rows": 6}))


from django.contrib.auth.models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    mobile = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user