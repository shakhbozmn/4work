from django import forms
from django.utils import timezone

from .models import Application, Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("title", "description", "budget", "deadline", "category", "skills")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input"}),
            "description": forms.Textarea(attrs={"rows": 6, "class": "form-input"}),
            "budget": forms.NumberInput(attrs={"class": "form-input", "step": "0.01"}),
            "deadline": forms.DateInput(attrs={"class": "form-input", "type": "date"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "skills": forms.CheckboxSelectMultiple(attrs={"class": "form-checkbox"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = self.fields["category"].queryset.order_by("name")
        self.fields["category"].empty_label = "Select a category"
        self.fields["skills"].queryset = self.fields["skills"].queryset.order_by("name")

    def clean_deadline(self):
        deadline = self.cleaned_data.get("deadline")
        if deadline is not None and deadline < timezone.localdate():
            raise forms.ValidationError("Deadline cannot be in the past.")
        return deadline


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("cover_letter", "proposed_timeline", "proposed_budget")
        widgets = {
            "cover_letter": forms.Textarea(attrs={"rows": 6, "class": "form-input"}),
            "proposed_timeline": forms.NumberInput(attrs={"class": "form-input", "min": "1"}),
            "proposed_budget": forms.NumberInput(attrs={"class": "form-input", "step": "0.01", "min": "0"}),
        }
