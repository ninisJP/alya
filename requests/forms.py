from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from accounting_order_sales.models import SalesOrderItem
from django import forms
from django.forms import inlineformset_factory

from logistic_suppliers.models import Suppliers



# Formulario para la creación de RequirementOrder (sin estado)
class CreateRequirementOrderForm(forms.ModelForm):
    class Meta:
        model = RequirementOrder
        fields = ['sales_order', 'requested_date', 'notes']  # El campo 'estado' se elimina

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
