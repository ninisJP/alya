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
    salesorder = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name="purchase_orders")
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    requested_date = models.DateField()
    requested_by = models.CharField(max_length=20, verbose_name="Encargado", blank=True, null=True)
    acepted = models.BooleanField(default=True)


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

import datetime
from django.db import transaction  # Para manejar la atomicidad

@classmethod
def create_from_requirement(cls, requirement_order):
    # Filtrar los ítems que están en estado "Comprando" (estado='C')
    items_to_purchase = requirement_order.items.filter(estado='C')

    # Validar que existan ítems para comprar
    if not items_to_purchase.exists():
        raise ValueError("No hay ítems en estado 'Comprando' para generar una orden de compra.")

    # Crear la orden de compra dentro de una transacción atómica
    with transaction.atomic():
        # Crear la orden de compra
        purchase_order = cls.objects.create(
            salesorder=requirement_order.sales_order,
            description=f"Orden de compra para {requirement_order.sales_order.sapcode}",
            requested_date=datetime.date.today(),  # Fecha actual como la fecha solicitada
            requested_by=requirement_order.user.username if requirement_order.user else "Desconocido",  # El encargado es el usuario que creó el requerimiento
            acepted=True  # Aceptamos la orden de compra por defecto
        )

        total_amount = Decimal('0.00')

        # Agregar cada ítem "Comprando" a la nueva orden de compra
        for item in items_to_purchase:
            total_price = item.sales_order_item.price * item.quantity_requested

            # Crear PurchaseOrderItem
            PurchaseOrderItem.objects.create(
                purchaseorder=purchase_order,
                sales_order_item=item.sales_order_item,
                sap_code=item.sales_order_item.sap_code,  # Código del producto
                class_pay=item.sales_order_item.class_pay,  # Método de pago
                type_pay=item.sales_order_item.type_pay,  # Tipo de pago
                quantity_requested=item.quantity_requested,
                notes=item.notes,  # Notas adicionales si las hubiera
                price=item.sales_order_item.price,  # Usar el precio de la SalesOrderItem
                price_total=total_price,  # Precio total
                mov_number="",  # Podrías asignar un número de movimiento si aplica
                bank=""  # El campo 'bank' es opcional
            )

            # Sumar el precio total al total de la orden de compra
            total_amount += total_price

        # Actualizar el monto total en la orden de compra (si tuvieses un campo `total_amount` en `PurchaseOrder`)
        # purchase_order.total_amount = total_amount
        purchase_order.save()

    return purchase_order

