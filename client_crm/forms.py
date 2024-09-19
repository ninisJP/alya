from django import forms
from .models import Contract

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ('client', 'contract_number', 'start_date', 'end_date', 'value', 'terms','contract_pdf')
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        labels = {
            'client': 'Cliente',
            'contract_number':'N° de Contrato',
            'start_date':'Fecha de Creación del Contrato',
            'end_date':'Fecha de Caducidad del Contrato',
            'value':'Valor del Contrato',
            'terms':'Términos',
            'contract_pdf': 'Contrato'
        }

