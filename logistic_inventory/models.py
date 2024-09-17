from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

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

class Subtype(models.Model):
    name = models.CharField(max_length=100)
    type = models.ForeignKey(Type, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True)
    description = models.CharField(max_length=100, null=True)
    item_id = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=0)
    subtype = models.ForeignKey(Subtype, on_delete=models.CASCADE, null=True)
    unit = models.CharField(max_length=100, null=True, blank=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    life_time = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return str(self.subtype.type)+" ("+str(self.subtype)+")"+" <"+str(self.description)+"> precio:"+str(self.price)+" precio por dia:"+str(self.price_per_day)+" vida: "+str(self.life_time)
