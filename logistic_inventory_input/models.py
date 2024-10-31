from django.db import models

# Create your models here.

from logistic_inventory_output.models import InventoryOutputItem

class InventoryInput(models.Model):
    output_item = models.OneToOneField(InventoryOutputItem, on_delete=models.CASCADE, primary_key=True)
    quantity = models.IntegerField(default=0)
    date_create = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inventario de Entrada"
        verbose_name_plural = "Inventarios de Entrada"

