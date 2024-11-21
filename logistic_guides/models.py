from decimal import Decimal
from django.db import models
from django.forms import ValidationError
from logistic_requirements.models import RequirementOrder, RequirementOrderItem

# Create your models here.
class ExitGuide(models.Model):
    requirement_order = models.ForeignKey(
        RequirementOrder,
        on_delete=models.CASCADE,
        related_name="exit_guides",
        verbose_name="Orden de Requerimiento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    total_items = models.PositiveIntegerField(default=0)

    def __str__(self):
        # Usar el ID directamente para representar la guía
        return f"Guía de Salida #{self.id} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Guía de Salida"
        verbose_name_plural = "Guías de Salida"



class ExitGuideItem(models.Model):
    exit_guide = models.ForeignKey(ExitGuide, on_delete=models.CASCADE, related_name="items", verbose_name="Guía de Salida")
    requirement_order_item = models.ForeignKey(RequirementOrderItem, on_delete=models.CASCADE, verbose_name="Ítem Orden de Requerimiento")
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal(0),
        verbose_name="Cantidad"
    )

    def clean(self):
        # Validar que no se retire más de lo solicitado en el RequirementOrderItem
        if self.quantity > self.requirement_order_item.quantity_requested:
            raise ValidationError(
                f"La cantidad para la guía de salida ({self.quantity}) no puede exceder la cantidad solicitada ({self.requirement_order_item.quantity_requested})."
            )

    def save(self, *args, **kwargs):
        # Validar antes de guardar
        self.clean()

        # Actualizar la cantidad restante del RequirementOrderItem
        requirement_item = self.requirement_order_item
        requirement_item.quantity_requested -= self.quantity
        if requirement_item.quantity_requested <= 0:
            requirement_item.estado = 'E'  # Cambiar a "Enviado" si ya no queda cantidad
        requirement_item.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.requirement_order_item.sales_order_item.description} - {self.quantity} unidades"

    class Meta:
        verbose_name = "Ítem Guía de Salida"
        verbose_name_plural = "Ítems Guías de Salida"
