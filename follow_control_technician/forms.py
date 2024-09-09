from django import forms
from employee.models import Technician
from .models import TechnicianTask, TechnicianCard, TechnicianCardTask
from django.forms import inlineformset_factory
from .models import TechnicianCard, TechnicianCardTask

class TechnicianTaskForm(forms.ModelForm):
    class Meta:
        model = TechnicianTask
        fields = ('verb', 'object', 'measurement', 'time')

        labels = {
            'verb': 'Verbo',
            'object': 'Objeto',
            'measurement': 'Und. Medida',
            'time': 'Tiempo',
        }

        widgets = {
            'verb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Verbo'}),
            'object': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objeto'}),
            'measurement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medida'}),
            'task_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tiempo'}),
        }

class TechnicianCardForm(forms.ModelForm):
    date = forms.DateField(
        label="Fecha de la Tarjeta",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Seleccione una fecha'})
    )

    technician = forms.ModelChoiceField(
        queryset=Technician.objects.all(),
        label="Técnico",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = TechnicianCard
        fields = ['technician', 'date']

# Formset para manejar las tareas asociadas a la tarjeta del técnico
TechnicianCardTaskFormSet = inlineformset_factory(
    TechnicianCard, 
    TechnicianCardTask, 
    fields=('task', 'quantity', 'saler_order', 'order'), 
    extra=5,
    widgets={
        'task': forms.Select(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
        'saler_order': forms.Select(attrs={'class': 'form-control'}),  
        'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Orden'}),
    }
)

