from django.db import models
from client.models import Client

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
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    budget_name = models.CharField(max_length=100, default="", verbose_name="Presupuesto")
    budget_days = models.PositiveIntegerField()
    budget_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_date = models.DateField()
    budget_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='budget_items')
    quantity = models.PositiveIntegerField()
    final_price = models.FloatField(default=0, blank=True)

    def __str__(self):
        return f'{self.item.description} - {self.quantity} unidades'

