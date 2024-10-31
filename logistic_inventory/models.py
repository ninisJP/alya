from django.db import models
from budget.models import CatalogItem


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"


class Type(models.Model):

    class Category(models.TextChoices):
        EQUIPO = 'Equipo'
        EPPS = 'EPPS'
        MATERIAL = 'Material'
        CONSUMIBLE = 'Consumible'
        HERRAMIENTA = 'Herramienta'

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=100, choices=Category.choices, default=Category.EQUIPO)

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = "Tipos"


class Subtype(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Subtipo"
        verbose_name_plural = "Subtipos"


class Item(models.Model):
    item = models.OneToOneField(CatalogItem, on_delete=models.CASCADE, primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=100, null=True)
    quantity = models.PositiveIntegerField(default=0)
    subtype = models.ForeignKey(Subtype, on_delete=models.CASCADE)
    unit = models.CharField(max_length=100, null=True, blank=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    life_time = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    code_qr = models.ImageField('img', upload_to='item_qr/', blank=True, null=True)

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
