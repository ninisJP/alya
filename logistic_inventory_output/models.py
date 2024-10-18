from django.db import models

from django.contrib.auth.models import User

from logistic_inventory.models import Item
from accounting_order_sales.models import SalesOrder


class InventoryOutput(models.Model):
    date_create = models.DateTimeField(auto_now_add=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.SET_NULL, null=True, blank=True)
    returned = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

class InventoryOutputItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True)
    output = models.ForeignKey(InventoryOutput, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(null=True, default=0)
