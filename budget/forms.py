from django import forms
from .models import Budget, BudgetItem, CatalogItem
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

class CatalogItemForm(forms.ModelForm):
    class Meta:
        model = CatalogItem
        fields = ('name', 'description', 'category', 'price', 'price_per_day')
        labels = {
            'name': 'Nombre del Item',
            'description': 'Descripcion',
            'category': 'Categoria',
            'price': 'Precio',
            'price_per_day': 'Precio por dia',
        }

class SearchCatalogItemForm(forms.Form):
    name = forms.CharField(label="name", max_length=100, required=False)
    description = forms.CharField(label="description", max_length=100, required=False)
