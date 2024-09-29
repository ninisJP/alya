from django.db import models
from django.core.validators import FileExtensionValidator
from project.models import Project
from client.models import Client
from decimal import Decimal

class SalesOrder(models.Model):
    sapcode = models.PositiveBigIntegerField(default=0)  # Código SAP por defecto como "000"
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)  # Proyecto puede ser nulo
    detail = models.CharField(max_length=255)
    date = models.DateField()

    def update_total_sales_order(self):
        self.total_sales_order = sum(item.price_total for item in self.items.all())
        self.save()

    def __str__(self):
        return f"{self.sapcode} - {self.project if self.project else 'Sin Proyecto'} - {self.detail}"


class SalesOrderItem(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="items")
    sap_code = models.CharField(max_length=50, default="")
    description = models.CharField(max_length=50, default="")
    amount = models.IntegerField(null=True, default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_total = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    unit_of_measurement = models.CharField(max_length=10, default="UND")
    remaining_requirement = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.description} - {self.amount} unidades"

    def update_remaining_requirement(self):
        cantidad_solicitada = sum(item.quantity_requested for item in self.requirementorderitem_set.all())
        self.remaining_requirement = self.amount - cantidad_solicitada
        self.save()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.salesorder.update_total_sales_order()


class PurchaseOrder(models.Model):
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE,related_name="purchase_orders")
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    requested_date = models.DateField()
    requested_by = models.CharField(max_length=20, verbose_name="Encargado", blank=True, null=True)
    acepted = models.BooleanField(default=True)

    def __str__(self):
        return f"Orden de Compra {self.id} para la Orden de Venta {self.salesorder.sapcode} - Solicitada el {self.requested_date}"

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