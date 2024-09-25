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
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    sap_code = models.CharField(max_length=50, default="")
    description = models.CharField(max_length=50, default="")
    amount = models.IntegerField(null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_of_measurement = models.CharField(max_length=10, default="UND")

    def __str__(self):
        return f"{self.description} - {self.amount} unidades"

class PurchaseOrder(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE,related_name="purchase_orders")
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    requested_date = models.DateField()
    requested_by = models.CharField(max_length=20, verbose_name="Encargado", blank=True, null=True)
    acepted = models.BooleanField(default=True)

    def __str__(self):
        return f"Purchase Order {self.id} for Sales Order {self.salesorder.sapcode} - Requested on {self.requested_date}"

class PurchaseOrderItem(models.Model):
    purchaseorder = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name="items")
    sales_order_item = models.ForeignKey(SalesOrderItem, on_delete=models.CASCADE)
    sap_code = models.CharField(max_length=50, default="")
    class_pay = models.CharField(max_length=50, default="")
    type_pay = models.CharField(max_length=50, default="")
    quantity_requested = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    mov_number = models.CharField(max_length=255, null=True, blank=True, default='')
    bank = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Item {self.sap_code} - {self.quantity_requested} units - Total {self.price_total}"


