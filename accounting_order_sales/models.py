from django.db import models
from django.core.validators import FileExtensionValidator
from project.models import Project
from client.models import Client
from decimal import Decimal


class SalesOrder(models.Model):
    sapcode = models.PositiveBigIntegerField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    detail = models.CharField(max_length=255)
    date = models.DateField()

    def __str__(self):
        return f"{self.sapcode} - {self.project} - {self.detail}"

class SalesOrderItem(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    sap_code = models.CharField(max_length=50, default="")
    description = models.CharField(max_length=50, default="")
    amount = models.IntegerField(null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_of_measurement = models.CharField(max_length=10, default="UND") 


    def __str__(self):
        return f"{self.description} - {self.amount} unidades"
