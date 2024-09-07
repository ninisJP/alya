from django import forms
from employee.models import Technician
from .models import TechnicianTask, TechnicianCard, TechnicianCardTask
from django.forms import inlineformset_factory
from .models import TechnicianCard, TechnicianCardTask


class TechnicianCardForm(forms.ModelForm):
    class Meta:
        model = TechnicianCard
        fields = ['technician', 'date']

TechnicianCardTaskFormSet = inlineformset_factory(
    TechnicianCard, 
    TechnicianCardTask, 
    fields=('task', 'quantity', 'saler_order', 'order'), 
    extra=1,  # Número de formularios extra para agregar nuevas tareas
    can_delete=True  # Permitir eliminar formularios
)
