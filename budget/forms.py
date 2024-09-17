from django import forms
from .models import Budget, BudgetItem
from django.forms import inlineformset_factory

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['client', 'budget_name', 'budget_days', 'budget_date']
        widgets = {
            'budget_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control', 
                'style': 'max-width: 200px;'  # Ajusta el tamaño aquí
            }),
        }
        labels = {
            'client': 'Cliente',
            'budget_name': 'Nombre del Presupuesto',
            'budget_days': 'Días del Presupuesto',
            'budget_date': 'Fecha del Presupuesto',
        }

BudgetItemFormSet = inlineformset_factory(
    Budget,
    BudgetItem,
    fields=['item', 'quantity'],
    extra=1,
    can_delete=True
)
