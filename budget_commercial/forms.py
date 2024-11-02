from django import forms

from budget.forms import Select2AjaxWidget
from .models import CommercialBudget, CommercialBudgetItem
from django.forms import inlineformset_factory

class CommercialBudgetForm(forms.ModelForm):
    class Meta:
        model = CommercialBudget
        fields = [
            'client', 'budget_type', 'budget_name', 'budget_number', 'budget_date'
        ]
        widgets = {
            'budget_date': forms.DateInput(attrs={'type': 'date'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'budget_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(CommercialBudgetForm, self).__init__(*args, **kwargs)
        self.fields['client'].empty_label = 'Seleccione un cliente'
        
        # Etiquetas en español
        self.fields['client'].label = 'Cliente'
        self.fields['budget_type'].label = 'Tipo de Presupuesto'
        self.fields['budget_name'].label = 'Nombre del Presupuesto'
        self.fields['budget_number'].label = 'Número del Presupuesto'
        self.fields['budget_date'].label = 'Fecha del Presupuesto'

class CommercialBudgetItemForm(forms.ModelForm):
    class Meta:
        model = CommercialBudgetItem
        fields = ('item', 'quantity', 'custom_price', 'unit')
        widgets = {
            'item': Select2AjaxWidget(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'custom_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Unitario'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidad de medida'}),
        }

    def __init__(self, *args, **kwargs):
        super(CommercialBudgetItemForm, self).__init__(*args, **kwargs)
        if 'DELETE' in self.fields:
            self.fields['DELETE'].widget = forms.HiddenInput()

        # Etiquetas en español para los campos
        self.fields['item'].label = 'Ítem'
        self.fields['quantity'].label = 'Cantidad'
        self.fields['custom_price'].label = 'Precio Unitario'
        self.fields['unit'].label = 'Unidad de Medida'

CommercialBudgetItemFormSet = inlineformset_factory(
    CommercialBudget,
    CommercialBudgetItem,
    form=CommercialBudgetItemForm,
    extra=0,
)
