from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from accounting_order_sales.models import SalesOrderItem
from django import forms
from django.forms import inlineformset_factory
from logistic_suppliers.models import Suppliers
from django.core.exceptions import ValidationError
from datetime import date, timedelta

# Formulario para la creación de RequirementOrder (sin estado)
class CreateRequirementOrderForm(forms.ModelForm):
    class Meta:
        model = RequirementOrder
        fields = ['sales_order', 'requested_date', 'notes']  # El campo 'estado' se elimina
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date', 'min': (date.today() + timedelta(days=3)).isoformat()}),
            'notes': forms.Textarea(attrs={'required': 'required'})
        }

    def clean_requested_date(self):
        requested_date = self.cleaned_data.get('requested_date')
        min_date = date.today() + timedelta(days=3) 
        if requested_date and requested_date < min_date:
            raise ValidationError(f"La fecha solicitada no puede ser anterior a {min_date.isoformat()}.")
        return requested_date
    
    def clean_notes(self):
        notes = self.cleaned_data.get('notes')
        if not notes.strip():
            raise ValidationError("El campo de notas es obligatorio.")
        return notes

# Formulario para la creación de RequirementOrderItem (sin estado)
# Formulario para la creación de RequirementOrderItem (sin estado)
class CreateRequirementOrderItemForm(forms.ModelForm):
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Precio Unitario",
        help_text="Dejar en blanco para usar el precio del ítem"
    )

    class Meta:
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested', 'notes', 'supplier', 'price', 'file_attachment']
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date', 'min': (date.today() + timedelta(days=3)).isoformat()}),
            'notes': forms.TextInput(attrs={'required': 'required', 'placeholder': 'Detalles (opcional)', 'class': 'form-control-sm'}),
        }


    def clean_requested_date(self):
        requested_date = self.cleaned_data.get('requested_date')
        min_date = date.today() + timedelta(days=3) 
        if requested_date and requested_date < min_date:
            raise ValidationError(f"La fecha solicitada no puede ser anterior a {min_date.isoformat()}.")
        return requested_date

    def __init__(self, *args, **kwargs):
        sales_order = kwargs.pop('sales_order', None)
        super().__init__(*args, **kwargs)

        if sales_order:
            self.fields['sales_order_item'].queryset = SalesOrderItem.objects.filter(salesorder=sales_order)
        
        self.fields['supplier'].queryset = Suppliers.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        sales_order_item = cleaned_data.get('sales_order_item')
        price = cleaned_data.get('price')

        if not price and sales_order_item:
            cleaned_data['price'] = sales_order_item.price

        return cleaned_data


# Creación de formset para manejar múltiples ítems
CreateRequirementOrderItemFormSet = inlineformset_factory(
    RequirementOrder,
    RequirementOrderItem,
    form=CreateRequirementOrderItemForm,
    extra=0,
    can_delete=True  # Permitir eliminar ítems en la creación
)


class PrepopulatedRequirementOrderItemForm(forms.ModelForm):
    class Meta:
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested']
        widgets = {
            'sales_order_item': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.sales_order = kwargs.pop('sales_order', None)
        super().__init__(*args, **kwargs)

        if self.sales_order:
            # Limit the queryset to items from the specific sales order
            self.fields['sales_order_item'].queryset = SalesOrderItem.objects.filter(salesorder=self.sales_order)

    def clean(self):
        cleaned_data = super().clean()
        sales_order_item = cleaned_data.get('sales_order_item')

        # Validate that the sales_order_item belongs to the sales_order
        if sales_order_item and self.sales_order and sales_order_item.salesorder != self.sales_order:
            raise ValidationError("El ítem de orden de venta no es válido.")

        return cleaned_data
