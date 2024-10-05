from django import forms
from accounting_order_sales.models import SalesOrder
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('verb', 'object', 'sale_order', 'measurement', 'task_time')  # Corregido: 'sale_order'
        labels = {
            'verb': 'Verbo',
            'object': 'Objeto',
            'sale_order': 'Orden de Venta',  # Corregido: 'sale_order'
            'measurement': 'Medida',
            'task_time': 'Tiempo',
        }
        widgets = {
            'verb': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Verbo'}),
            'object': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objeto'}),
            'sale_order': forms.Select(attrs={'class': 'form-control'}),  # Corregido: 'sale_order'
            'measurement': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Medida'}),
            'task_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Tiempo'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar la etiqueta de cada opción en el select para incluir el detalle de la orden de venta y el nombre del cliente
        self.fields['sale_order'].label_from_instance = lambda obj: (
            f'{obj.detail} - {obj.project.client.legal_name}' 
            if obj.project and obj.project.client else f'{obj.detail} - Sin Cliente'
        )

