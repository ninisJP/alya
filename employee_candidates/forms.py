from django import forms
from .models import Candidate

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'department', 'birth_date', 'salary_expectation', 'phone', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'department': forms.TextInput(attrs={'placeholder': 'Área o departamento'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha de nacimiento'}),
            'salary_expectation': forms.NumberInput(attrs={'placeholder': 'Pretensión salarial'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Número de celular'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
        }
