from django import forms
from .models import SIPOC, SIPOCRow
from django import forms
from .models import Supplier, Input, Process, Output, Customer


class SIPOCForm(forms.ModelForm):
    class Meta:
        model = SIPOC
        fields = ['name']  # Puedes añadir más campos si fuera necesario
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del SIPOC'}),
        }
        labels = {
            'name': 'Nombre del SIPOC',
        }

class SIPOCRowForm(forms.ModelForm):
    class Meta:
        model = SIPOCRow
        fields = ['suppliers', 'inputs', 'processes', 'outputs', 'customers']
        widgets = {
            'suppliers': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple', 
                'data-placeholder': 'Seleccione proveedores'
            }),
            'inputs': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple', 
                'data-placeholder': 'Seleccione entradas'
            }),
            'processes': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple', 
                'data-placeholder': 'Seleccione procesos'
            }),
            'outputs': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple', 
                'data-placeholder': 'Seleccione salidas'
            }),
            'customers': forms.SelectMultiple(attrs={
                'class': 'form-control select2-multiple', 
                'data-placeholder': 'Seleccione clientes'
            }),
        }
        labels = {
            'suppliers': 'Proveedores',
            'inputs': 'Entradas',
            'processes': 'Procesos',
            'outputs': 'Salidas',
            'customers': 'Clientes',
        }
        
class SIPOCRowSuppliersForm(forms.ModelForm):
    class Meta:
        model = SIPOCRow
        fields = ['suppliers']
        widgets = {
            'suppliers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'suppliers': 'Proveedores',
        }

class SIPOCRowInputsForm(forms.ModelForm):
    class Meta:
        model = SIPOCRow
        fields = ['inputs']
        widgets = {
            'inputs': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'inputs': 'Entradas',
        }

class SIPOCRowProcessesForm(forms.ModelForm):
    class Meta:
        model = SIPOCRow
        fields = ['processes']
        widgets = {
            'processes': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'processes': 'Procesos',
        }

class SIPOCRowOutputsForm(forms.ModelForm):
    class Meta:
        model = SIPOCRow
        fields = ['outputs']
        widgets = {
            'outputs': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'outputs': 'Salidas',
        }

class SIPOCRowCustomersForm(forms.ModelForm):
    class Meta:
        model = SIPOCRow
        fields = ['customers']
        widgets = {
            'customers': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'customers': 'Clientes',
        }

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'name': 'Nombre del Proveedor'}

class InputForm(forms.ModelForm):
    class Meta:
        model = Input
        fields = ['content']
        widgets = {'content': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'content': 'Entrada'}

class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['step']
        widgets = {'step': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'step': 'Proceso'}

class OutputForm(forms.ModelForm):
    class Meta:
        model = Output
        fields = ['result']
        widgets = {'result': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'result': 'Salida'}

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}
        labels = {'name': 'Nombre del Cliente'}
