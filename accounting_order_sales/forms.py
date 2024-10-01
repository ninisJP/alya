from django import forms
from .models import SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem
from django.forms import inlineformset_factory

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

class ItemSalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrderItem
        fields = ['sap_code', 'description', 'amount', 'price', 'price_total', 'unit_of_measurement']
        widgets = {
            'sap_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SAP Code'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Description'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Amount'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Price'
            }),
            'price_total': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total Price'
            }),
            'unit_of_measurement': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unit of Measurement (e.g. UND)'
            }),
        }

class ItemSalesOrderExcelForm(forms.Form):
    excel_file = forms.FileField(label='Selecciona un archivo Excel', widget=forms.ClearableFileInput(attrs={
        'class': 'form-control',
        'placeholder': 'Selecciona un archivo Excel'
    }))

# Formulario para la orden de compra (PurchaseOrder)
class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = ['scheduled_date']  # Campos editables
        widgets = {
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

# Formulario para los ítems de la orden de compra (PurchaseOrderItem)
class PurchaseOrderItemForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderItem
        fields = ['sales_order_item', 'quantity_requested', 'price', 'supplier', 'class_pay', 'type_pay', 'notes']  # Campos editables
        widgets = {
            'sales_order_item': forms.Select(attrs={'class': 'form-select'}),
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': forms.Select(attrs={'class': 'form-select select2'}),
            'class_pay': forms.Select(attrs={'class': 'form-select'}),
            'type_pay': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }
