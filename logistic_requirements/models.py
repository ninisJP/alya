from django.db import models
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from django.utils import timezone
from django.contrib.auth.models import User
from logistic_suppliers.models import Suppliers
from django.core.exceptions import ValidationError

class RequirementOrder(models.Model):
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="requirement_orders")
    requested_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    estado = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_order = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_order_created = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        # Obtener los SalesOrderItems afectados antes de eliminar
        affected_sales_order_items = set(item.sales_order_item for item in self.items.all())

        # Eliminar la RequirementOrder y sus items
        super().delete(*args, **kwargs)

        # Recalcular remaining_requirement para cada SalesOrderItem afectado
        for sales_order_item in affected_sales_order_items:
            sales_order_item.update_remaining_requirement()

    def __str__(self):
        return f"Requirement Order {self.order_number} for {self.sales_order.sapcode} on {self.requested_date}"

    def save(self, *args, **kwargs):
        # Si es una nueva instancia, guardarla primero para generar el ID
        if not self.pk:
            super().save(*args, **kwargs)
            self.order_number = f"OR-{self.id}"  # Generar el número de orden basado en el ID

        # Calcular el total de la orden sumando los precios de los ítems
        self.total_order = sum(item.total_price for item in self.items.all())
        
        # Guardar finalmente la instancia
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
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, blank=True, null=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    #pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)

    def clean(self):
    # Obtener la cantidad solicitada original si el ítem ya existe
        if self.pk:
            original_quantity = RequirementOrderItem.objects.get(pk=self.pk).quantity_requested
            # Si no hay cambio en la cantidad, saltar la validación
            if self.quantity_requested <= self.sales_order_item.remaining_requirement + original_quantity:
                return
        else:
            original_quantity = 0

        # Validar si la cantidad solicitada es mayor que la cantidad disponible,
        # teniendo en cuenta la cantidad original en caso de ser una edición
        if (self.sales_order_item.remaining_requirement + original_quantity) < self.quantity_requested:
            raise ValidationError(
                f"La cantidad solicitada ({self.quantity_requested}) excede la cantidad disponible ({self.sales_order_item.remaining_requirement})."
            )
        super().clean()
        
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.sales_order_item.price
        if not self.sap_code:
            self.sap_code = self.sales_order_item.sap_code

        super().save(*args, **kwargs)
        self.sales_order_item.update_remaining_requirement()

    def delete(self, *args, **kwargs):
        sales_order_item = self.sales_order_item
        super().delete(*args, **kwargs)
        sales_order_item.update_remaining_requirement()

    def __str__(self):
        return f"{self.sales_order_item.description} ({self.quantity_requested}) - {self.get_estado_display()}"

    @property
    def total_price(self):
        return self.price * self.quantity_requested




