from django import forms
from django.conf import settings

from accounting_order_sales.models import SalesOrderItem
from logistic_inventory.models import Item

from logistic_inventory_output.models import InventoryOutput, InventoryOutputItem


class SearchOutputItemForm(forms.Form):
	sap_code = forms.CharField(label="SAP", max_length=100, required=False)

class RetornedOutputItemForm(forms.Form):
	quantity = forms.IntegerField(label="Cantidad")
