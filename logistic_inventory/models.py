from django.db import models
from datetime import datetime

class Category(models.Model):
    CATEGORY_CHOICES = [
        ('EQUIPOS', 'Equipos'),
        ('EPPS', 'EPPS'),
        ('MATERIALES', 'Materiales'),
        ('CONSUMIBLES', 'Consumibles'),
        ('HERRAMIENTAS', 'Herramientas'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES)

    def __str__(self):
        return self.get_name_display()

class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ProductType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    product_id = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    unit = models.CharField(max_length=100)
    unit_measure = models.DecimalField(max_digits=12, decimal_places=2, default=0)
