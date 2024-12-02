from django import forms

from .models import SalesOrder, SalesOrderItem, PurchaseOrder, PurchaseOrderItem,Bank, CollectionOrders

from django.forms import inlineformset_factory
from django.http import JsonResponse
from django import forms
from logistic_suppliers.models import Suppliers
from django.urls import reverse_lazy

from . import models

class SupplierSelect2Widget(forms.Select):
    class Media:
        css = {'all': ('https://cdn.jsdelivr.net/npm/select2@4.1.0/dist/css/select2.min.css',)}
        js = (
            'https://code.jquery.com/jquery-3.7.1.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0/dist/js/select2.min.js',
        )

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['class'] = (attrs.get('class', '') + ' select2-ajax').strip()
        attrs['data-placeholder'] = 'Selecciona un proveedor'
        attrs['data-ajax--url'] = reverse_lazy('supplier_autocomplete')
        attrs['style'] = 'width: 100%;'
        return attrs

def supplier_autocomplete(request):
    term = request.GET.get('term', '')
    suppliers = Suppliers.objects.filter(name__icontains=term)[:20]
    supplier_list = [{'id': supplier.id, 'text': supplier.name} for supplier in suppliers]
    return JsonResponse({'results': supplier_list})

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
    archivo_excel = forms.FileField(label='Selecciona un archivo Excel', widget=forms.ClearableFileInput(attrs={
        'class': 'form-control',
        'placeholder': 'Selecciona un archivo Excel'
    }))



# Bank
class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = ['bank_name', 'bank_account', 'bank_detail', 'bank_current_mount']


class UploadBankStatementForm(forms.Form):
    bank = forms.ModelChoiceField(queryset=Bank.objects.all(), required=True, label='Bank')
    excel_file = forms.FileField(label='Excel File')


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
        fields = ['quantity_requested', 'price', 'supplier', 'class_pay', 'type_pay', 'notes']  # Removed 'sales_order_item'
        widgets = {
            'quantity_requested': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'supplier': SupplierSelect2Widget(),  # Cambiado para usar AJAX
            'class_pay': forms.Select(attrs={'class': 'form-select'}),
            'type_pay': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }


# Form for collection orders
class CollectionOrdersForm(forms.ModelForm):
    class Meta:
        model = CollectionOrders
        fields = [
            'orden_venta', 'serie_correlativo', 'fecha_emision', 'cliente',
            'ruc_cliente', 'tipo_moneda', 'descripcion', 'importe_total',
            'detraccion', 'monto_neto_cobrar', 'total_cuotas', 'fecha_vencimiento',
            'tipo_cobro', 'desc_factoring', 'extracto_banco', 'factura_pagado'
        ]

class BankLoanForm(forms.ModelForm):
    class Meta:
        model = models.BankLoan
        fields = ('start_date', 'desembols_date', 'bank', 'detail','currency', 'cuotas', 'document', 'total_debt', 'credit_type')

        labels = {
                'start_date'    : 'Fecha de inicio',
                'desembols_date': 'Fecha de desembolso',
                'bank'          : 'Banco',
                'detail'       : 'Detalles',
                'currency'      : 'Moneda (USD, PEN)',
                'cuotas'        : 'Cuotas',
                'document'      : 'Documento asociado',
                'total_debt'    : 'Deuda total',
                'credit_type'   : 'Tipo de credito',
        }

class LoanPaymentForm(forms.ModelForm):
    class Meta:
        model = models.LoanPayment
        fields = ('amount', 'pay_date')

        labels = {
                'amount'    : 'Monto',
                'pay_date'  : 'Fecha de pago',
        }

class PartialPaymentForm(forms.ModelForm):
    class Meta:
        model = models.PartialPayment
        fields = ('loan_payment', 'partial_amount', 'receipt', 'receipt_date')
        labels = {
                'loan_payment'  : 'Cuota',
                'partial_amount': 'Monto',
                'receipt'       : 'Recibo',
                'receipt_date'  : 'Fecha',
        }

    def __init__(self, *args, **kwargs):
        loan = kwargs.pop('loan')
        super(PartialPaymentForm, self).__init__(*args, **kwargs)

        self.fields['loan_payment'].queryset = models.LoanPayment.objects.filter(loan=loan, is_paid=False)

class SearchLoanForm(forms.Form):
    bank = forms.CharField(label="Banco", max_length=100, required=False)
