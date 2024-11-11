from django import forms
from .models import TaskNote

class TaskNoteForm(forms.ModelForm):
    class Meta:
        model = TaskNote
        fields = ['title', 'description', 'urgency_level', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Titulo de requerimiento o bugs'}),
            'description': forms.Textarea(attrs={'placeholder': 'Descripción del requerimiento / bug', 'rows': 3}),
            'urgency_level': forms.Select(attrs={'placeholder': 'Nivel de urgencia'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha a considerar'}),
        }
