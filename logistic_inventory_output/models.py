from django.db import models

from django.contrib.auth.models import User

from logistic_inventory.models import Item
from accounting_order_sales.models import SalesOrder


class InventoryOutput(models.Model):
    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, primary_key=True)
    date_create = models.DateTimeField(auto_now_add=True)

class InventoryOutputItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    output = models.ForeignKey(InventoryOutput, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_create = models.DateTimeField(auto_now_add=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)
