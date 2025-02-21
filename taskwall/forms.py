# See LICENSE file for copyright and license details.
"""
Task Note Forms
"""
from django import forms
from .models import TaskNote


class TaskNoteForm(forms.ModelForm):
    """ Task Note Form """
    class Meta:
        """
        Form TaskNoteForm
        form to record requirements or task wall
        Parameters:
        ---------------------------------------
        title(str): Title of the task
        description(str): Description of the task
        urgency_level(int): Urgency level of the task
        due_date(date): Due date of the task
        """
        model = TaskNote
        fields = ['title', 'description', 'urgency_level', 'due_date']
        widgets = {
            'title': forms.TextInput(
                attrs={'placeholder': 'Titulo de requerimiento o bugs'}),
            'description': forms.Textarea(
                attrs={'placeholder': 'Descripción del requerimiento / bug',
                       'rows': 3}),
            'urgency_level': forms.Select(
                attrs={'placeholder': 'Nivel de urgencia'}),
            'due_date': forms.DateInput(
                attrs={'type': 'date', 'placeholder': 'Fecha a considerar'}),
        }
