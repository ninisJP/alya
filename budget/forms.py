from django import forms
from .models import Budget, BudgetItem
from django.forms import inlineformset_factory


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['budget_name', 'budget_days', 'budget_price', 'budget_final_price', 'budget_date']
        widgets = {
            'budget_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

BudgetItemFormSet = inlineformset_factory(
    Budget,
    BudgetItem,
    fields=['item', 'quantity', 'measurement', 'final_price'],
    extra=1,
    can_delete=True
)
