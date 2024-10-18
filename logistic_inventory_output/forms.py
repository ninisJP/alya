from django import forms
from django.conf import settings

from logistic_inventory.models import Item
from accounting_order_sales.models import SalesOrderItem

from .models import InventoryOutput, InventoryOutputItem

class InventoryOutputForm(forms.ModelForm):
    class Meta:
        model = InventoryOutput
        fields = ('sales_order',)
        labels = {
            'sales_order': 'Orden de venta',
        }

    def save(self, commit=True):
        instance = super(InventoryOutputForm, self).save(commit=False)
        if commit:
            instance.save()
            # Create QR
            all_items = SalesOrderItem.objects.filter(salesorder=instance.sales_order)
            for item in all_items:
                inventory_item = Item.objects.filter(item_id=item.sap_code)
                item_save = InventoryOutputItem(item=inventory_item[0], output=instance, quantity=item.amount)
                item_save.save()

        return instance

class SearchSalesOrderForm(forms.Form):
    sapcode = forms.CharField(label="SAP", max_length=100, required=False)
    project = forms.CharField(label="Proyecto", max_length=100, required=False)
    detail = forms.CharField(label="Description", max_length=100, required=False)
