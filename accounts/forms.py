from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile, User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))

    class Meta:
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-input"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "hourly_rate", "avatar", "skills", "company_name")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "skills": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Role-based field filtering
        if user is not None:
            if user.role == "client":
                self.fields.pop("hourly_rate", None)
                self.fields.pop("skills", None)
            elif user.role == "freelancer":
                self.fields.pop("company_name", None)
        for field_name, field in self.fields.items():
            if field_name not in ("skills",):
                field.widget.attrs["class"] = "form-input"
