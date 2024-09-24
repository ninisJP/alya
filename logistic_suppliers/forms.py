from django import forms
from .models import Suppliers

class SuppliersForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = ('document', 'name', 'bank', 'account', 'currency', 'interbank_currency')
        labels = {
            'document': 'RUC/DNI',
            'name': 'Nombre del Proveedor',
            'bank': 'Nombre del Banco',
            'account': 'Número de Cuenta',
            'currency': 'Moneda',
            'interbank_currency': 'Número de Cuenta Interbancario',
        }
        widgets = {
            'document': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'RUC/DNI'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Proveedor'}),
            'bank': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Banco'}),
            'account': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de Cuenta'}),
            'currency': forms.Select(attrs={'class': 'form-control'}),
            'interbank_currency': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de Cuenta Interbancario'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
