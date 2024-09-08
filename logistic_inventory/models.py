from django.db import models
from datetime import datetime

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('EQUIPOS', 'Equipos'),
        ('EPPS', 'EPPS'),
        ('TRANSPORTE', 'Transporte'),
        ('MATERIALES', 'Materiales'),
        ('CONSUMIBLES', 'Consumibles'),
        ('ALIMENTOS', 'Alimentos'),
        ('MANODEOBRA', 'Mano de Obra'),
        ('HERRAMIENTAS', 'Herramientas'),
        ('MISC', 'Misc'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.get_name_display()

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    measurement = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class VariantProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    daily_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.producto.nombre} - {self.marca.nombre}'

class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    ]

    variant_product = models.ForeignKey(VariantProduct, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(default=datetime.now)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == 'SALIDA':
            if self.variant_product.quantity < self.quantity:
                raise ValueError("No hay suficiente stock para realizar la salida.")
            self.variant_product.quantity -= self.quantity
        elif self.transaction_type == 'ENTRADA':
            self.variant_product.quantity += self.quantity

        self.variant_product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.transaction_type} - {self.variant_product.product.name} - {self.quantity} unidades'
