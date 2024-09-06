from django import forms
from .models import Technician, TechnicianTask, TechnicianCard, TechnicianCardTask

class TechnicianForm(forms.ModelForm):
    class Meta:
        model = Technician
        fields = ['name', 'lastname', 'email', 'rank', 'technician_class']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rank': forms.TextInput(attrs={'class': 'form-control'}),
            'technician_class': forms.TextInput(attrs={'class': 'form-control'}),
        }

class TechnicianTaskForm(forms.ModelForm):
    class Meta:
        model = TechnicianTask
        fields = ['verb', 'object', 'measurement', 'time']
        widgets = {
            'object': forms.TextInput(attrs={'class': 'form-control'}),
            'verb': forms.TextInput(attrs={'class': 'form-control'}),
            'measurement': forms.TextInput(attrs={'class': 'form-control'}),
            'time': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class TechnicianCardForm(forms.ModelForm):
    tasks = forms.ModelMultipleChoiceField(
        queryset=TechnicianTask.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'size': '15'
        })
    )

    class Meta:
        model = TechnicianCard
        fields = ['technician', 'station', 'date', 'tasks']
        widgets = {
            'technician': forms.Select(attrs={'class': 'form-control'}),
            'station': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def save_m2m(self):
        tasks = self.cleaned_data.get('tasks')
        for task in tasks:
            TechnicianCardTask.objects.create(
                technician_card=self.instance,
                task=task,
                order=TechnicianCardTask.objects.filter(technician_card=self.instance).count() + 1
            )