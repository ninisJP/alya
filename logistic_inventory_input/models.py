from django.db import models

from logistic_inventory_output.models import InventoryOutputItem

class InventoryInput(models.Model):
    output_item = models.OneToOneField(InventoryOutputItem, on_delete=models.CASCADE, primary_key=True)
    quantity = models.IntegerField(default=0)
    date_create = models.DateTimeField(auto_now_add=True)
