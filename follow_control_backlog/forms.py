# forms.py

from django import forms
from follow_control_card.models import Task

class CardTaskForm(forms.Form):
    tasks = forms.ModelMultipleChoiceField(
        queryset=Task.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
        label='Tareas Disponibles'
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(CardTaskForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['tasks'].queryset = Task.objects.filter(user=user)
