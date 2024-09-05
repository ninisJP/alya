from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'client')
        labels = {
            'name': 'Proyecto',
            'client':'Cliente',
        }
