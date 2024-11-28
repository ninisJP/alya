from django.db import models
from accounting_order_sales.models import SalesOrder, SalesOrderItem
from django.utils import timezone
from django.contrib.auth.models import User
from logistic_suppliers.models import Suppliers
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from decimal import Decimal
from django.db.models import Sum
from django.core.exceptions import ValidationError

class RequirementOrder(models.Model):
    STATE_CHOICES = [
        ('APROBADO', 'Aprobado'),
        ('RECHAZADO', 'Rechazado'),
        ('NO REVISADO', 'No Revisado')
    ]
    sales_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="requirement_orders")
    requested_date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    order_number = models.CharField(max_length=20, unique=True, blank=True)
    estado = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    total_order = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    purchase_order_created = models.BooleanField(default=False)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='NO REVISADO')

    def delete(self, *args, **kwargs):
        affected_sales_order_items = set(item.sales_order_item for item in self.items.all())
        super().delete(*args, **kwargs)

        for sales_order_item in affected_sales_order_items:
            sales_order_item.update_remaining_requirement()

    def save(self, *args, **kwargs):
        # Verificar si el estado cambia a 'RECHAZADO'
        if self.pk:
            previous_state = RequirementOrder.objects.get(pk=self.pk).state
            if previous_state != 'RECHAZADO' and self.state == 'RECHAZADO':
                # Rechazar todos los ítems y actualizar la cantidad disponible
                for item in self.items.all():
                    item.estado = 'R'
                    item.save()

        # Generación de order_number si la instancia es nueva
        if not self.pk:
            super().save(*args, **kwargs)
            self.order_number = f"OR-{self.id}"

        # Calcula el total de la orden sumando los precios de los ítems
        self.total_order = sum(item.total_price for item in self.items.all())

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Requirement Order {self.order_number} for {self.sales_order.sapcode} on {self.requested_date}"

    class Meta:
        verbose_name = "Orden de Requerimiento"
        verbose_name_plural = "Ordenes de Requerimiento"

class RequirementOrderItem(models.Model):
    ESTADO_CHOICES = [
        ('L', 'Listo'),
        ('P', 'Pendiente'),
        ('C', 'Comprando'),
        ('R', 'Rechazado'),
        ('E', 'Enviado'),
        ('A', 'Aceptado'),
    ]
    requirement_order = models.ForeignKey(RequirementOrder, on_delete=models.CASCADE, related_name="items")
    sales_order_item = models.ForeignKey(SalesOrderItem, on_delete=models.CASCADE)
    sap_code = models.CharField(max_length=50, default="")
    quantity_requested = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(1))
    quantity_requested_remaining = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal(1))
    notes = models.CharField(max_length=255, blank=True, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.SET_NULL, blank=True, null=True)
    estado = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    file_attachment = models.FileField(
        upload_to='attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        help_text="Sube un archivo PDF o una imagen (JPG, PNG)."
    )

    @property
    def remaining_quantity(self):
        """Cantidad restante por enviar."""
        sent_quantity = self.exitguideitem_set.aggregate(
            total_sent=Sum('quantity')
        )['total_sent'] or Decimal(0)  # Considera 0 si no hay envíos
        return self.quantity_requested - sent_quantity

    def save(self, *args, **kwargs):
        # Si el ítem es nuevo, inicializar quantity_requested_remaining con quantity_requested
        if not self.pk:  # Es un nuevo ítem
            self.quantity_requested_remaining = self.quantity_requested
        else:
            # Verificamos si el estado ha cambiado a 'Rechazado' y ajustamos la cantidad en el sales_order_item
            original_item = RequirementOrderItem.objects.get(pk=self.pk)
            if self.estado == 'R' and original_item.estado != 'R':
                # Si el estado cambia a 'Rechazado', devolvemos la cantidad solicitada al sales_order_item
                self.sales_order_item.remaining_requirement += self.quantity_requested_remaining
            elif self.estado != 'R' and original_item.estado == 'R':
                # Si el estado cambió de 'Rechazado' a otro estado, restamos la cantidad al sales_order_item
                self.sales_order_item.remaining_requirement -= self.quantity_requested_remaining

        # Establecer valores por defecto si no están definidos
        if not self.price:
            self.price = self.sales_order_item.price
        if not self.sap_code:
            self.sap_code = self.sales_order_item.sap_code

        super().save(*args, **kwargs)
        # Actualizamos el remaining_requirement de sales_order_item después de guardar
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

    class Meta:
        verbose_name = "Item Orden de Requerimiento"
        verbose_name_plural = "Items Orden de Requerimiento"

