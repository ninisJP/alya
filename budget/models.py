from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Item(models.Model):
    CLASS_CHOICES = [
        ('herramienta', 'Herramienta'),
        ('material', 'Material'),
        ('consumible', 'Consumible'),
    ]

    description = models.CharField(max_length=255, verbose_name="Descripción")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Unitario")
    daily_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Diario")
    lifespan = models.PositiveIntegerField(verbose_name="Tiempo de Vida (días)")
    item_class = models.CharField(max_length=50, choices=CLASS_CHOICES, verbose_name="Clase de Ítem")

    def __str__(self):
        return f'{self.description} - {self.unit_price} por unidad'

class Budget(models.Model):
    budget_name = models.CharField(max_length=100, default="", verbose_name="Presupuesto")
    budget_days = models.PositiveIntegerField()
    budget_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_date = models.DateField()

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='budget_items')
    quantity = models.PositiveIntegerField()
    measurement = models.CharField(max_length=50, blank=True, default='')
    final_price = models.FloatField(default=0, blank=True)  # Añadir blank=True aquí

    def __str__(self):
        return f'{self.item.description} - {self.quantity} unidades'

