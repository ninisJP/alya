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

# Formulario para RequirementOrderItem
# Formulario para RequirementOrderItem
class RequirementOrderItemForm(forms.ModelForm):
    class Meta:
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested', 'supplier', 'notes', 'estado']  # Se añade el campo 'supplier'
        widgets = {
            'estado': forms.Select(choices=RequirementOrderItem.ESTADO_CHOICES),  # Se renderiza como un select con las opciones
            'supplier': forms.Select()  # El campo supplier se renderiza como un select
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si quieres personalizar el queryset de suppliers, puedes hacerlo aquí
        self.fields['supplier'].queryset = Suppliers.objects.all()

# Creación de formset para manejar múltiples ítems
RequirementOrderItemFormSet = inlineformset_factory(
    RequirementOrder,
    RequirementOrderItem,
    form=RequirementOrderItemForm,
    extra=0,  # No permitir ítems adicionales
    can_delete=False  # No permitir eliminar ítems
)
