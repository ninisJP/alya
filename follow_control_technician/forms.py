from django import forms
from employee.models import Technician
from .models import TechnicianTask, TechnicianCard, TechnicianCardTask
from django.forms import inlineformset_factory
from .models import TechnicianCard, TechnicianCardTask, TechnicianTaskGroup, TechnicianTaskGroupItem

class TechnicianTaskForm(forms.ModelForm):
    class Meta:
        model = TechnicianTask
        fields = ('verb', 'object', 'measurement', 'time', 'rutine','frecuency')

        labels = {
            'verb': 'Verbo',
            'object': 'Objeto',
            'measurement': 'Und. Medida',
            'time': 'Tiempo',
            'rutine':'Rutina',
            'frecuency': 'Frecuencia',
        }

        widgets = {
            'verb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Verbo'}),
            'object': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objeto'}),
            'measurement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'unidad de medida'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'placeholder': 'tiempo'}),
            'rutine': forms.Select(attrs={'class': 'form-control' , 'placeholder': 'Rutina'}),
            'frecuency': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Frecuencia'})
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
        'task': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Tarea'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
        'saler_order': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Orden de Venta'}),
        'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Orden'}),
    }
)

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Selecciona un archivo Excel")

class TechnicianCardTaskForm(forms.ModelForm):
    class Meta: 
        model = TechnicianCardTask
        fields = ['task', 'quantity', 'saler_order']

class TechnicianTaskGroupForm(forms.ModelForm):
    class Meta:
        model = TechnicianTaskGroup
        fields = ['name']

class TechnicianTaskGroupItemForm(forms.ModelForm):
    class Meta:
        model = TechnicianTaskGroupItem
        fields = ['task', 'quantity', 'saler_order']

class AddTasksToGroupForm(forms.Form):
    tasks = forms.ModelMultipleChoiceField(
        queryset=TechnicianTask.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Opcional: Cambia según tu preferencia
        label="Seleccionar Tareas"
    )
    search = forms.CharField(
        required=False,
        label="Buscar tarea",
        widget=forms.TextInput(attrs={'placeholder': 'Buscar tarea...', 'class': 'form-control'})
    )

class EditGroupItemForm(forms.ModelForm):
    class Meta:
        model = TechnicianTaskGroupItem
        fields = ['quantity', 'saler_order', 'order']

        labels = {
            'quantity': 'Cantidad',
            'saler_order': 'Orden de Venta',
            'order': 'Orden en el Grupo',
        }

        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'saler_order': forms.Select(attrs={'class': 'form-control'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }

