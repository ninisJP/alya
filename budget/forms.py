# See LICENSE file for copyright and license details.
"""
Form budget to see by admin
"""
from django import forms
from django.forms import inlineformset_factory
from django.urls import reverse_lazy

from .models import Budget, BudgetItem, CatalogItem


class Select2AjaxWidget(forms.Select):
    """
    Ajax to dinamic select in form
    """
    class Media:
        css = {
            'all': ('',
            )
        }
        js = (
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0/dist/js/select2.min.js',
        )

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['class'] = (attrs.get('class', '') + ' select2-ajax').strip()
        attrs['data-placeholder'] = 'Seleccione un ítem'
        attrs['data-ajax--url'] = reverse_lazy('catalog_item_search')
        attrs['style'] = 'width: 100%;'
        return attrs


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'client', 'budget_name', 'budget_number', 'budget_days', 'budget_date',
            'budget_expenses', 'budget_utility', 'budget_deliverytime',
            'budget_servicetime', 'budget_warrantytime'
        ]
        widgets = {
            'budget_date': forms.DateInput(attrs={'type': 'date'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        self.fields['client'].empty_label = 'Seleccione un cliente'

        # Etiquetas en español
        self.fields['client'].label = 'Cliente'
        self.fields['budget_name'].label = 'Nombre del Presupuesto'
        self.fields['budget_number'].label = 'Número del Presupuesto'
        self.fields['budget_days'].label = 'Días del Presupuesto'
        self.fields['budget_date'].label = 'Fecha del Presupuesto'
        self.fields['budget_expenses'].label = 'Gastos'
        self.fields['budget_utility'].label = 'Utilidad'
        self.fields['budget_deliverytime'].label = 'Tiempo de Entrega'
        self.fields['budget_servicetime'].label = 'Tiempo de Servicio'
        self.fields['budget_warrantytime'].label = 'Tiempo de Garantía'

class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ('item', 'quantity', 'custom_price', 'custom_price_per_day', 'unit')
        widgets = {
            'item': Select2AjaxWidget(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'custom_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Unitario'}),
            'custom_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio por Día'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidad de medida'}),
        }

    def __init__(self, *args, **kwargs):
        super(BudgetItemForm, self).__init__(*args, **kwargs)
        if 'DELETE' in self.fields:
            self.fields['DELETE'].widget = forms.HiddenInput()

        # Etiquetas en español para los campos
        self.fields['item'].label = 'Ítem'
        self.fields['quantity'].label = 'Cantidad'
        self.fields['custom_price'].label = 'Precio Unitario'
        self.fields['custom_price_per_day'].label = 'Precio por Día'
        self.fields['unit'].label = 'Unidad de Medida'


# Configuración del formset
BudgetItemFormSet = inlineformset_factory(
    Budget,
    BudgetItem,
    form=BudgetItemForm,
    extra=0,
)

class NewBudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ('item', 'quantity', 'custom_price', 'custom_price_per_day', 'unit')
        widgets = {
            'item': Select2AjaxWidget(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'custom_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Unitario'}),
            'custom_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio por Día'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidad de medida'}),
        }

    def __init__(self, *args, **kwargs):
        super(NewBudgetItemForm, self).__init__(*args, **kwargs)
        # Configura las etiquetas en español
        self.fields['item'].label = 'Ítem'
        self.fields['quantity'].label = 'Cantidad'
        self.fields['custom_price'].label = 'Precio Unitario'
        self.fields['custom_price_per_day'].label = 'Precio por Día'
        self.fields['unit'].label = 'Unidad de Medida'

class BudgetUploadForm(forms.Form):
    excel_file = forms.FileField(label='Subir Excel')

class BudgetEditNewForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'client', 'budget_name', 'budget_number', 'budget_days', 'budget_date',
            'budget_expenses', 'budget_utility', 'budget_deliverytime',
            'budget_servicetime', 'budget_warrantytime'
        ]
        widgets = {
            'budget_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'budget_name': forms.TextInput(attrs={'class': 'form-control'}),
            'budget_number': forms.TextInput(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'budget_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'budget_expenses': forms.Select(attrs={'class': 'form-control'}),
            'budget_utility': forms.Select(attrs={'class': 'form-control'}),
            'budget_deliverytime': forms.Select(attrs={'class': 'form-control'}),
            'budget_servicetime': forms.NumberInput(attrs={'class': 'form-control'}),
            'budget_warrantytime': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiquetas personalizadas en español
        self.fields['client'].label = 'Cliente'
        self.fields['budget_name'].label = 'Nombre del Presupuesto'
        self.fields['budget_number'].label = 'Número del Presupuesto'
        self.fields['budget_days'].label = 'Días del Presupuesto'
        self.fields['budget_date'].label = 'Fecha del Presupuesto'
        self.fields['budget_expenses'].label = 'Gastos (%)'
        self.fields['budget_utility'].label = 'Utilidad (%)'
        self.fields['budget_deliverytime'].label = 'Tiempo de Entrega'
        self.fields['budget_servicetime'].label = 'Tiempo de Servicio'
        self.fields['budget_warrantytime'].label = 'Tiempo de Garantía'

class CatalogItemForm(forms.ModelForm):
    class Meta:
        model = CatalogItem
        fields = ('sap', 'description', 'category', 'price', 'price_per_day', 'unit')
        labels = {
            'sap': 'SAP',
            'description': 'Nombre',
            'category': 'Categoria',
            'price': 'Precio',
            'price_per_day': 'Precio por día',
            'unit': 'Unidad de medida',
        }

class SearchCatalogItemForm(forms.Form):
    sap = forms.CharField(label="sap", max_length=100, required=False)
    description = forms.CharField(label="description", max_length=100, required=False)

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Selecciona el archivo Excel")

class AddBudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['item', 'quantity', 'custom_price', 'custom_price_per_day']
        widgets = {
            'item': Select2AjaxWidget(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'custom_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Unitario'}),
            'custom_price_per_day': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio por Día'}),
        }

    def __init__(self, *args, **kwargs):
        super(AddBudgetItemForm, self).__init__(*args, **kwargs)
        self.fields['item'].label = 'Ítem'
        self.fields['quantity'].label = 'Cantidad'
        self.fields['custom_price'].label = 'Precio Unitario'
        self.fields['custom_price_per_day'].label = 'Precio por Día'

class EditBudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['quantity', 'custom_price', 'custom_price_per_day']

class AddBudgetItemPlus(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ['item', 'quantity', 'unit','custom_price', 'custom_price_per_day','coin']
        widgets = {
            'item': Select2AjaxWidget(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidad de medida'}),
            'custom_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio Unitario'}),
            'coin': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(AddBudgetItemPlus, self).__init__(*args, **kwargs)
        self.fields['item'].label = 'Ítem'
        self.fields['quantity'].label = 'Cantidad'
        self.fields['unit'].label = 'Unidad de medida'
        self.fields['custom_price'].label = 'Precio Unitario'

class BudgetPlusForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = [
            'client', 'budget_name', 'budget_days', 'budget_date',
            'budget_expenses'
        ]
        widgets = {
            'budget_date': forms.DateInput(attrs={
                'type': 'date', 'class': 'form-control'
            }),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'budget_name': forms.TextInput(attrs={'class': 'form-control'}),
            'budget_days': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].empty_label = 'Seleccione un cliente'

        # Etiquetas en español
        self.fields['client'].label = 'Cliente'
        self.fields['budget_name'].label = 'Nombre del Presupuesto'
        self.fields['budget_days'].label = 'Días del Presupuesto'
        self.fields['budget_date'].label = 'Fecha del Presupuesto'
