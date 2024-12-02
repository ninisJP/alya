from django import forms
from django.forms import inlineformset_factory

from logistic_suppliers.models import Suppliers
from .models import RequirementOrder, RequirementOrderItem

# Formulario para RequirementOrder
class RequirementOrderForm(forms.ModelForm):
    class Meta:
        model = RequirementOrder
        fields = ['sales_order', 'requested_date', 'notes', 'estado']  # Se añade el campo 'estado'
        widgets = {
            'estado': forms.CheckboxInput(),  # Se renderiza como un checkbox
        }

# Search Forms para RequirementOrder

class RequirementOrderListForm(forms.ModelForm):
	
	class Meta:
		model = RequirementOrder
		fields = ['order_number','notes', 'estado']         


# Formulario para RequirementOrderItem
class RequirementOrderItemForm(forms.ModelForm):
    item_name = forms.CharField(
        label="Descripción del Ítem",
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
    )

    class Meta:
        model = RequirementOrderItem
        fields = ['item_name', 'quantity_requested', 'supplier', 'notes', 'estado']
        widgets = {
            'estado': forms.Select(choices=RequirementOrderItem.ESTADO_CHOICES),
            'supplier': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegúrate de cargar el valor descriptivo en el campo `item_name`
        if self.instance and self.instance.sales_order_item:
            self.fields['item_name'].initial = str(self.instance.sales_order_item)  # Aquí cargamos el nombre descriptivo





# Creación de formset para manejar múltiples ítems
RequirementOrderItemFormSet = inlineformset_factory(
    RequirementOrder,
    RequirementOrderItem,
    form=RequirementOrderItemForm,
    extra=0,  # No permitir ítems adicionales
    can_delete=False  # No permitir eliminar ítems
)
