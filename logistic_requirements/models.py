from django.db import models
from accounting_order_sales.models import PurchaseOrder, PurchaseOrderItem, SalesOrder, SalesOrderItem
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
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.SET_NULL, null=True, blank=True)

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
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'pdf',
                    'jpg',
                    'jpeg',
                    'png',
                    'zip',
                    'rar',
                    'docx',
                    'xlsx',
                    'csv'
                ]
            )
        ],
        help_text="Sube un archivo PDF o una imagen (JPG, PNG)."
    )
    date_purchase_order = models.DateField(null=True, blank=True)
    purchase_order_created = models.BooleanField(default=False)


    @property
    def is_paid(self):
        """Método para obtener el estado de pago del PurchaseOrderItem relacionado con el SalesOrderItem."""
        try:
            purchase_order_item = self.sales_order_item.purchaseorderitem_set.first()  # Suponiendo una relación inversa
            if purchase_order_item:
                return purchase_order_item.payment_status == 'Pagado'
        except PurchaseOrderItem.DoesNotExist:
            return False
        return False

    @property
    def remaining_quantity(self):
        """Cantidad restante por enviar."""
        sent_quantity = self.exitguideitem_set.aggregate(
            total_sent=Sum('quantity')
        )['total_sent'] or Decimal(0)  # Considera 0 si no hay envíos
        return self.quantity_requested - sent_quantity

    def clean(self):
        """Validación personalizada para el precio total."""
        # Validar que el total solicitado no exceda el total permitido por el `SalesOrderItem`
        if self.sales_order_item:
            total_permitido = self.sales_order_item.price_total
            total_solicitado = self.total_price

            # TODO: Revisar si es necesario agregar un margen de tolerancia, hablar con el inge.
            if float(total_solicitado) > (float(total_permitido)+0.10):
                raise ValidationError(
                    f"El total solicitado ({total_solicitado}) excede el total permitido ({total_permitido}) para el ítem '{self.sales_order_item.description}'."
                )

    def save(self, *args, **kwargs):
        # Llama al método `clean()` para validar antes de guardar
        self.clean()
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
        if not self.price:
            self.price = 0
        return round(self.price * self.quantity_requested, 2)

    class Meta:
        verbose_name = "Item Orden de Requerimiento"
        verbose_name_plural = "Items Orden de Requerimiento"

