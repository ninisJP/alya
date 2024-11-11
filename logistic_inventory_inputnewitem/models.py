from django.db import models

from accounting_order_sales.models import PurchaseOrderItem
from logistic_inventory.models import Item

class InventoryInputNewItem(models.Model):
	purchase_item = models.OneToOneField(PurchaseOrderItem, on_delete=models.CASCADE, primary_key=True)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=0)
	date_create = models.DateTimeField(auto_now_add=True)
