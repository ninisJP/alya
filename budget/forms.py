from django import forms
from .models import Budget, BudgetItem, CatalogItem
from django.forms import inlineformset_factory
from django import forms
from django.urls import reverse_lazy

class Select2AjaxWidget(forms.Select):
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/select2@4.1.0/dist/css/select2.min.css',)
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


class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ('item', 'quantity')
        widgets = {
            'item': Select2AjaxWidget(),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(BudgetItemForm, self).__init__(*args, **kwargs)
        if 'DELETE' in self.fields:
            self.fields['DELETE'].widget = forms.HiddenInput()

BudgetItemFormSet = inlineformset_factory(
    Budget,
    BudgetItem,
    form=BudgetItemForm,
    extra=0,
)

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