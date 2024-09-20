from django import forms
from django.forms import inlineformset_factory
from .models import RequirementOrder, RequirementOrderItem

# Formulario para RequirementOrder
class RequirementOrderForm(forms.ModelForm):
    class Meta:
        model = RequirementOrder
        fields = ['sales_order', 'requested_date', 'notes']

# Formulario para RequirementOrderItem
class RequirementOrderItemForm(forms.ModelForm):
    class Meta:
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested', 'notes']

# Creación de formset para manejar múltiples ítems
RequirementOrderItemFormSet = inlineformset_factory(
    RequirementOrder,
    RequirementOrderItem,
    form=RequirementOrderItemForm,
    extra=1,
    can_delete=True
)
