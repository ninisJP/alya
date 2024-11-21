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
        ExitGuideItem.objects.create(
            exit_guide=exit_guide,
            requirement_order_item=item,
            quantity=item.quantity_requested
        )

    # Actualizar el total de ítems en la guía
    exit_guide.total_items = ready_items.count()
    exit_guide.save()

    return exit_guide
