from django.db import models

from django.contrib.auth.models import User

from logistic_inventory.models import Item
from accounting_order_sales.models import SalesOrder
from logistic_requirements.models import RequirementOrderItem


class InventoryOutput(models.Model):
    sale_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, primary_key=True)
    date_create = models.DateTimeField(auto_now_add=True)
    returned = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Inventario de Salida"
        verbose_name_plural = "Inventario de Salida"


class InventoryOutputItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    item_requirement = models.ForeignKey(RequirementOrderItem, on_delete=models.CASCADE, related_name="input")
    output = models.ForeignKey(InventoryOutput, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    date_create = models.DateTimeField(auto_now_add=True)
    date_returned = models.DateTimeField(null=True, blank=True)
    returned = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Item Inventario Salida"
        verbose_name_plural = "Items Inventario Salida"
