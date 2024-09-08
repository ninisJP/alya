from django import forms
from .models import SalesOrder

class SalesOrderForm(forms.ModelForm):
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Seleccione una fecha'})
    )
    
    class Meta:
        model = SalesOrder
        fields = ["sapcode", "project",  "detail", "date"]
        widgets = {
            'sapcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código SAP'}),
            'project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Proyecto'}),
            'detail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalle'}),
        }

