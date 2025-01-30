# See LICENSE file for copyright and license details.
"""
Requests Forms
"""
from datetime import date, timedelta

from django import forms
from django.forms import inlineformset_factory
from django.core.exceptions import ValidationError

from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from accounting_order_sales.models import SalesOrderItem
from logistic_suppliers.models import Suppliers


class CreateRequirementOrderForm(forms.ModelForm):
    """"
    Form for creating RequirementOrder (stateless)

    Fields
    ------
    sales_order: sapcode number
    requested_date: date of the request
    notes: additional notes

    Condition
    ---------
    requested_date: only tuesday and wednesday are allowed
    """
    class Meta:
        """
        Additional options the form to create a request order
        """
        model = RequirementOrder
        fields = ['sales_order', 'requested_date', 'notes']
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date', 'min': (
                date.today() + timedelta(days=0)).isoformat()}
            ),
            'notes': forms.Textarea(attrs={'required': 'required'})
        }

    def clean_requested_date(self):
        """
        Prohibits users from requesting an order on Tuesdays and Wednesdays

        Parameters
        ----------
        requested_date: date

        Returns
        -------
        request_date:
            date requested except Tuesday and Wednesday
        """
        requested_date = self.cleaned_data.get('requested_date')

        # Validar solo martes y miercoles (weekday 1 y 2), bloquearlos
        if requested_date.weekday() == 1:  # Martes
            raise forms.ValidationError(
                "No puedes solicitar el pedido los martes." +
                " Selecciona otra fecha.")
        if requested_date.weekday() == 2:  # Miercoles
            raise forms.ValidationError(
                "No puedes solicitar el pedido los miercoles." +
                " Selecciona otra fecha.")

        return requested_date


# Formulario para la creación de RequirementOrderItem (sin estado)
class CreateRequirementOrderItemForm(forms.ModelForm):
    """
    Form for creating RequirementOrderItemForm (stateless)
    """
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Precio Unitario",
        help_text="Dejar en blanco para usar el precio del ítem"
    )

    class Meta:
        """
        Additional options the form to create a request order item

        Fields
        ------
        sales_order_item: item to request
        quantity_requested: quantity requested
        notes: additional notes
        supplier: supplier
        price: price
        file_attachment: file_attachment

        Widgets
        -------
        requested_date: dateInput
        notes: textInput
        """
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested',
                  'notes', 'supplier', 'price', 'file_attachment']
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date', 'min': (
                date.today() +
                timedelta(days=3)
                ).isoformat()}),
            'notes': forms.TextInput(
                attrs={'required': 'required',
                       'placeholder': 'Detalles (opcional)',
                       'class': 'form-control-sm'}
                ),
        }

    def __init__(self, *args, **kwargs):
        """
        Excludes items that reached zero stock

        Fields
        ------
        remaining_requirement__gt: remaining requirement greater than 0

        Returns
        -------
        only items available
        """
        sales_order = kwargs.pop('sales_order', None)
        super().__init__(*args, **kwargs)

        if sales_order:
            # pylint: disable=no-member
            self.fields['sales_order_item'].queryset = (
                SalesOrderItem.objects.filter(
                    salesorder=sales_order,
                    remaining_requirement__gt=0,)
            )
        # pylint: disable=no-member
        self.fields['supplier'].queryset = Suppliers.objects.all()

    def clean(self):
        """
        If the item price has not been added in the form,
        the price in the catalog will be added by default.

        Returns:
            cleaned_data: float or default: catalog price
        """
        cleaned_data = super().clean()
        sales_order_item = cleaned_data.get('sales_order_item')
        price = cleaned_data.get('price')

        if not price and sales_order_item:
            cleaned_data['price'] = sales_order_item.price

        return cleaned_data


# inlineformset_factory allows you to add,
# edit and delete objects related to a model
CreateRequirementOrderItemFormSet = inlineformset_factory(
    RequirementOrder,
    RequirementOrderItem,
    form=CreateRequirementOrderItemForm,
    extra=0,
    can_delete=True  # Permitir eliminar ítems en la creación
)


class PrepopulatedRequirementOrderItemForm(forms.ModelForm):
    """
    Form for creating RequirementOrderItemForm (stateless)

    Fields
    ------
    sales_order_item: item to request
    quantity_requested: float
        quantity requested
    notes: str
        additional notes

    Widgets
    -------
    sales_order_item: HiddenInput
    notes: TextInput
    """
    class Meta:
        """
        Additional options the form to create a request order item
        """
        model = RequirementOrderItem
        fields = ['sales_order_item', 'quantity_requested', 'notes']
        widgets = {
            'sales_order_item': forms.HiddenInput(),
            'notes': forms.TextInput(attrs={
                'placeholder': 'Detalles adicionales (opcional)',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.sales_order = kwargs.pop('sales_order', None)
        super().__init__(*args, **kwargs)

        if self.sales_order:
            # Limita el queryset a ítems específicos de la orden de venta
            # pylint: disable=no-member
            self.fields['sales_order_item'].queryset = (
                SalesOrderItem.objects.filter(salesorder=self.sales_order))

    def clean(self):
        """
        Validates that the sales order item belongs to the correct order
        """
        cleaned_data = super().clean()
        sales_order_item = cleaned_data.get('sales_order_item')

        if sales_order_item and self.sales_order:
            if sales_order_item.salesorder != self.sales_order:
                error = "El ítem de orden de venta no es válido."
                raise ValidationError(error)
        return cleaned_data
