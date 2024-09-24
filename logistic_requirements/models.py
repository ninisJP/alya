from django.db import models
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from django.utils import timezone
from django.contrib.auth.models import User

class RequirementOrder(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="requirement_orders")
    requested_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    estado = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_order = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Requirement Order {self.order_number} for {self.sales_order.sapcode} on {self.requested_date}"

    def save(self, *args, **kwargs):
        # Si el order_number no existe, guardarlo para obtener el ID primero
        if not self.pk:
            super().save(*args, **kwargs)  # Guarda inicialmente para obtener el id
            self.order_number = f"OR-{self.id}"  # Genera el número de orden basado en el id
            super().save(*args, **kwargs)  # Vuelve a guardar para asignar el order_number

        # Calcular el total después de que la instancia tenga un ID
        self.total_order = sum(item.price * item.quantity_requested for item in self.items.all())

        # Guardar nuevamente con el total actualizado
        super().save(*args, **kwargs)

class RequirementOrderItem(models.Model):
    ESTADO_CHOICES = [
        ('L', 'Listo'),
        ('P', 'Pendiente'),
        ('C', 'Comprando')
    ]
    requirement_order = models.ForeignKey(RequirementOrder, on_delete=models.CASCADE, related_name="items")
    sales_order_item = models.ForeignKey(SalesOrderItem, on_delete=models.CASCADE)
    sap_code = models.CharField(max_length=50, default="")
    quantity_requested = models.PositiveIntegerField(default=1)
    notes = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Si el precio no está definido, asignarlo desde sales_order_item
        if not self.price:
            self.price = self.sales_order_item.price
        if not self.sap_code:
            self.sap_code = self.sales_order_item.sap_code
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.sales_order_item.description} ({self.quantity_requested}) - {self.get_estado_display()}"

    # Método para calcular el precio total de un ítem (cantidad * precio unitario)
    @property
    def total_price(self):
        return self.price * self.quantity_requested

