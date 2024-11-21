from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from logistic_guides.models import ExitGuide, ExitGuideItem
from logistic_requirements.models import RequirementOrder
from django.db.models import F, ExpressionWrapper, DecimalField

from django.db.models import Sum, Subquery, OuterRef, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def create_exit_guide_view(request, requirement_order_id):
    # Obtener la orden de requerimiento
    requirement_order = get_object_or_404(RequirementOrder, pk=requirement_order_id)

    # Filtrar los ítems en estado 'Listo'
    ready_items = requirement_order.items.filter(estado='L')

    if not ready_items.exists():
        messages.info(request, "No hay ítems listos para enviar.")
        return redirect('requirement_order_detail', pk=requirement_order_id)

    # Crear la guía de salida
    exit_guide = ExitGuide.objects.create(
        requirement_order=requirement_order,
        description="Guía de salida generada automáticamente"
    )

    # Crear los ítems en la guía de salida
    for item in ready_items:
        ExitGuideItem.objects.create(
            exit_guide=exit_guide,
            requirement_order_item=item,
            quantity=item.quantity_requested
        )
        # Actualizar estado del ítem
        item.estado = 'E'
        item.save()

    # Mensaje de éxito
    messages.success(request, "Guía de salida creada exitosamente.")
    return redirect('requirement_order_detail', pk=requirement_order_id)
