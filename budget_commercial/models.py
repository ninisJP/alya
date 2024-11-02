from django.db import models
from decimal import Decimal
from budget.models import CatalogItem
from client.models import Client


class CommercialBudget(models.Model):
    class BudgetType(models.TextChoices):
        PURCHASE = 'Compra', 'Compra'
        SALE = 'Venta', 'Venta'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True)
    budget_type = models.CharField(max_length=10, choices=BudgetType.choices, default=BudgetType.PURCHASE)
    budget_name = models.CharField(max_length=100, default="")
    budget_number = models.CharField(max_length=10, blank=True)
    budget_date = models.DateField()
    budget_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_final_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def calculate_budget_price(self):
        return sum(item.total_price for item in self.items.all())

    def calculate_final_price(self):
        return self.budget_price  # Si no tienes descuentos adicionales, el precio final es el mismo.

    def save(self, *args, **kwargs):
        # Solo calcula el precio si la instancia ya tiene un ID asignado
        if self.pk:
            self.budget_price = self.calculate_budget_price()
            self.budget_final_price = self.calculate_final_price()
        
        super().save(*args, **kwargs)  # Guarda la instancia

    def __str__(self):
        return f'{self.budget_name} - {self.budget_type}'

    class Meta:
        verbose_name = "Presupuesto Comercial"
        verbose_name_plural = "Presupuestos Comerciales"


class CommercialBudgetItem(models.Model):
    budget = models.ForeignKey(CommercialBudget, on_delete=models.CASCADE, related_name='commercial_items')
    item = models.ForeignKey(CatalogItem, on_delete=models.CASCADE, related_name='commercial_budget_items')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    custom_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, blank=True)
    unit = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Si no se ha especificado un precio personalizado, utiliza el precio del catálogo
        if self.custom_price is None:
            self.custom_price = self.item.price

        # Calcular el precio total basado en el precio unitario y la cantidad
        price = Decimal(self.custom_price)
        self.total_price = price * Decimal(self.quantity)

        super().save(*args, **kwargs)
        # Guardar el presupuesto para actualizar los valores de precio total
        self.budget.save()

    def __str__(self):
        return f'{self.item} - {self.quantity} {self.unit}'

    class Meta:
        verbose_name = "Item de Presupuesto Comercial"
        verbose_name_plural = "Items de Presupuesto Comercial"

