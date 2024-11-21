from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import F, ExpressionWrapper, DecimalField, Sum, Subquery, OuterRef
from django.db.models.functions import Coalesce
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from logistic_guides.models import ExitGuide, ExitGuideItem
from logistic_requirements.models import RequirementOrder


def create_exit_guide_view(request, requirement_order_id):
    """
    Vista para crear una guía de salida desde una orden de requerimiento.
    """
    # Obtener la orden de requerimiento
    requirement_order = get_object_or_404(RequirementOrder, pk=requirement_order_id)

    # Actualizar `quantity_requested_remaining` para todos los ítems de la orden
    for item in requirement_order.items.all():
        if item.quantity_requested_remaining != item.quantity_requested:
            item.quantity_requested_remaining = item.quantity_requested
            item.save()

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

    total_items = 0  # Contador para los ítems procesados

    # Crear los ítems en la guía de salida
    for item in ready_items:
        # Validar que haya cantidad restante disponible
        if item.quantity_requested <= 0:
            messages.error(request, f"No hay cantidad disponible para el ítem {item.sales_order_item.description}.")
            continue

        # Usar la cantidad solicitada como referencia
        quantity_to_send = item.quantity_requested

        # Crear el ítem de la guía de salida
        ExitGuideItem.objects.create(
            exit_guide=exit_guide,
            requirement_order_item=item,
            quantity=quantity_to_send
        )

        # Actualizar la cantidad restante
        item.quantity_requested_remaining -= quantity_to_send

        # Actualizar estado del ítem si ya no queda cantidad restante
        if item.quantity_requested_remaining <= 0:
            item.estado = 'E'

        item.save()
        total_items += 1

    # Actualizar el total de ítems en la guía
    exit_guide.total_items = total_items
    exit_guide.save()

    if total_items > 0:
        messages.success(request, "Guía de salida creada exitosamente.")
    else:
        messages.warning(request, "No se pudo procesar ningún ítem para la guía de salida.")

    return redirect('requirement_order_detail', pk=requirement_order_id)


def list_requirement_order_guides(request, requirement_order_id):
    requirement_order = get_object_or_404(RequirementOrder, pk=requirement_order_id)
    guides = ExitGuide.objects.filter(requirement_order=requirement_order)

    return render(
        request,
        'guides/requirement_order_guides_list.html',  # Nota: faltaba una coma aquí
        {
            'requirement_order': requirement_order,
            'guides': guides,
        }
    )

def export_exit_guide_pdf(request, guide_id):
    """
    Genera un PDF con los detalles de una guía de salida específica.
    """
    # Obtener la guía de salida
    guide = get_object_or_404(ExitGuide, pk=guide_id)

    # Crear una respuesta HTTP con tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="guia_salida_{guide.id}.pdf"'

    # Crear el canvas para el PDF
    buffer = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Título del documento
    buffer.setFont("Helvetica-Bold", 16)
    buffer.drawString(200, height - 50, f"Guía de Salida #{guide.id}")
    buffer.setFont("Helvetica", 12)
    buffer.drawString(50, height - 80, f"Fecha: {guide.created_at.strftime('%d/%m/%Y')}")
    buffer.drawString(50, height - 100, f"Descripción: {guide.description or 'Sin descripción'}")

    # Espacio para la tabla
    data = [["Código SAP", "Descripción", "Cantidad", "Unidad de Medida", "Categoría"]]

    # Agregar los ítems de la guía a la tabla
    for item in guide.items.all():
        data.append([
            item.requirement_order_item.sales_order_item.sap_code,
            item.requirement_order_item.sales_order_item.description,
            str(item.quantity),
            item.requirement_order_item.sales_order_item.unit_of_measurement,
            item.requirement_order_item.sales_order_item.category,
        ])

    # Crear la tabla
    table = Table(data, colWidths=[80, 150, 80, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Calcular posición inicial para la tabla
    table.wrapOn(buffer, width, height)
    table.drawOn(buffer, 50, height - 300)

    # Pie de página
    buffer.setFont("Helvetica-Oblique", 10)
    buffer.drawString(50, 50, f"Guía de salida generada el {guide.created_at.strftime('%d/%m/%Y')}.")

    # Finalizar el PDF
    buffer.showPage()
    buffer.save()

    return response

