from django import forms
from .models import SalesOrder

class SalesOrderForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'Seleccione una fecha'})
    )
    
    class Meta:
        model = SalesOrder
        fields = ["sapcode", "project", "detail", "date"]
        widgets = {
            'sapcode': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Código SAP'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'detail': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Detalle'}),
        }

