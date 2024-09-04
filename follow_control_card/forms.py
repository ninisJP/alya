from django import forms

from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('verb', 'object', 'orden_venta', 'client', 'measurement', 'task_time')

        labels = {
            'verb': 'Verbo',
            'object': 'Objeto',
            'orden_venta': 'Orden de Venta',
            'client': 'Cliente',
            'measurement': 'Medida',
            'task_time': 'Tiempo',
        }

        widgets = {
            'verb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Verbo'}),
            'object': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objeto'}),
            'orden_venta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Orden de Venta'}),
            'client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cliente'}),
            'measurement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medida'}),
            'task_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tiempo'}),
        }
