from decimal import Decimal
from django.db import models
from django.forms import ValidationError
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from django.contrib.auth.models import User

class ExitGuide(models.Model):
    requirement_order = models.ForeignKey(
        RequirementOrder,
        on_delete=models.CASCADE,
        related_name="exit_guides",
        verbose_name="Orden de Requerimiento"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True, blank=True)
    departure_point = models.CharField(max_length=255, null=True, blank=True, verbose_name="Punto de Partida")
    arrival_point = models.CharField(max_length=255, null=True, blank=True, verbose_name="Punto de Llegada")
    transfer_reason = models.CharField(max_length=255, null=True, blank=True, verbose_name="Motivo del Traslado")
    transport_vehicle = models.CharField(max_length=255, null=True, blank=True, verbose_name="Movilidad de Traslado")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega")
    obs = models.TextField(null=True, blank=True, verbose_name="Observaciones")
    responsible_person = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="exit_guides",
        verbose_name="Encargado"
    )

    def __str__(self):
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
        # Validar que no se retire más de la cantidad restante
        if self.quantity > self.requirement_order_item.quantity_requested_remaining:
            raise ValidationError(
                f"La cantidad para la guía de salida ({self.quantity}) no puede exceder la cantidad restante ({self.requirement_order_item.quantity_requested_remaining})."
            )

    def save(self, *args, **kwargs):
        # Validar antes de guardar
        self.clean()

        # Actualizar la cantidad restante en RequirementOrderItem
        requirement_item = self.requirement_order_item
        requirement_item.quantity_requested_remaining -= self.quantity
        if requirement_item.quantity_requested_remaining < 0:
            requirement_item.quantity_requested_remaining = 0
        requirement_item.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Restaurar la cantidad restante en RequirementOrderItem al eliminar
        requirement_item = self.requirement_order_item
        requirement_item.quantity_requested_remaining += self.quantity
        requirement_item.save()

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.requirement_order_item.sales_order_item.description} - {self.quantity} unidades"

    class Meta:
        verbose_name = "Ítem Guía de Salida"
        verbose_name_plural = "Ítems Guías de Salida"

