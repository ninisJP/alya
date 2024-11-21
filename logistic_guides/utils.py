from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from logistic_requirements.models import RequirementOrder
from .models import ExitGuide, ExitGuideItem

def create_exit_guide(requirement_order_id):
    requirement_order = get_object_or_404(RequirementOrder, pk=requirement_order_id)

    # Filtrar ítems en estado "Listo"
    ready_items = requirement_order.items.filter(estado='L')

    if not ready_items.exists():
        raise ValidationError("No hay ítems en estado 'Listo' para crear una guía de salida.")

    # Crear la guía de salida
    exit_guide = ExitGuide.objects.create(requirement_order=requirement_order)

    # Crear los ítems de la guía de salida
    for item in ready_items:
        # Validar que haya cantidad restante disponible
        if item.quantity_requested_remaining <= 0:
            raise ValidationError(
                f"No hay cantidad disponible para el ítem {item.sales_order_item.description}."
            )

        # Usar la cantidad restante para la guía
        quantity_to_send = item.quantity_requested_remaining

        ExitGuideItem.objects.create(
            exit_guide=exit_guide,
            requirement_order_item=item,
            quantity=quantity_to_send
        )

        # Actualizar la cantidad restante
        item.quantity_requested_remaining -= quantity_to_send

        # Actualizar estado del ítem si ya no queda cantidad
        if item.quantity_requested_remaining <= 0:
            item.estado = 'E'

        item.save()

    # Actualizar el total de ítems en la guía
    exit_guide.total_items = ready_items.count()
    exit_guide.save()

    return exit_guide

