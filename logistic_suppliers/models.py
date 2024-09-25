from django.db import models
from .utils import CURRENCY_CHOICES

# Create your models here.
class Suppliers(models.Model):
    document = models.CharField(max_length=20, unique=True, verbose_name="RUC/DNI", null=True, blank=True, default='')
    name = models.CharField(max_length=100, verbose_name="Nombre del Proveedor", null=True, blank=True, default='')
    bank = models.CharField(max_length=100, verbose_name="Nombre del Banco", null=True, blank=True, default='')
    account = models.CharField(max_length=50, verbose_name="Número de Cuenta", null=True, blank=True, default='')
    currency = models.CharField(choices=CURRENCY_CHOICES, default="Soles", verbose_name="Moneda", null=True, blank=True)
    interbank_currency = models.CharField(max_length=50, verbose_name="Número de Cuenta Interbancario", null=True, blank=True, default='')

    def __str__(self):
        return f"{self.name} - {self.document}"

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
