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
    class Meta:
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested', 'notes', 'supplier']  # Añade 'supplier'

    def __init__(self, *args, **kwargs):
        sales_order = kwargs.pop('sales_order', None)  # Obtener la orden de venta si se pasa
        super().__init__(*args, **kwargs)

        # Si hay una orden de venta, filtrar los ítems
        if sales_order:
            self.fields['sales_order_item'].queryset = SalesOrderItem.objects.filter(salesorder=sales_order)

        # Puedes establecer el queryset para el campo supplier si es necesario
        self.fields['supplier'].queryset = Suppliers.objects.all()  # Ajusta según necesites



# Creación de formset para manejar múltiples ítems
CreateRequirementOrderItemFormSet = inlineformset_factory(
    RequirementOrder,
    RequirementOrderItem,
    form=CreateRequirementOrderItemForm,
    extra=0,
    can_delete=True  # Permitir eliminar ítems en la creación
)
