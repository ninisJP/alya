from django.db import models
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from django.utils import timezone

class RequirementOrder(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    requested_date = models.DateField()  # Fecha en la que necesitas los ítems
    notes = models.TextField(blank=True, null=True)  # Campo opcional para agregar notas
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática

    def __str__(self):
        return f"Requirement Order for {self.sales_order.sapcode} on {self.requested_date}"

class RequirementOrderItem(models.Model):
    requirement_order = models.ForeignKey(RequirementOrder, on_delete=models.CASCADE, related_name="items")
    sales_order_item = models.ForeignKey(SalesOrderItem, on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True, null=True)  # Campo para agregar notas cortas

    def __str__(self):
        return f"{self.sales_order_item.description} ({self.quantity_requested})"

