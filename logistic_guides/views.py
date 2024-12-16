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
from django.db import transaction
from django.core.exceptions import ValidationError

def create_exit_guide_view(request, requirement_order_id):
    """
    Vista para crear una guía de salida desde una orden de requerimiento.
    """
    requirement_order = get_object_or_404(RequirementOrder, pk=requirement_order_id)

    # Filtrar ítems en estado 'Listo'
    ready_items = requirement_order.items.filter(estado='L')

    if not ready_items.exists():
        messages.info(request, "No hay ítems listos para enviar.")
        return redirect('requirement_order_detail', pk=requirement_order_id)

    # Crear la guía de salida
    with transaction.atomic():  # Garantizar consistencia en la transacción
        exit_guide = ExitGuide.objects.create(
            requirement_order=requirement_order,
            description="Guía de salida generada automáticamente"
        )

        total_items = 0  # Contador para los ítems procesados

        for item in ready_items:
            # Usar la cantidad restante como referencia
            try:
                quantity_to_send = item.remaining_quantity
                if quantity_to_send > 0:
                    ExitGuideItem.objects.create(
                        exit_guide=exit_guide,
                        requirement_order_item=item,
                        quantity=quantity_to_send
                    )
                    total_items += 1
            except ValidationError as e:
                messages.error(request, f"Error al procesar {item.sales_order_item.description}: {e.message}")

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

from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def export_exit_guide_pdf(request, guide_id):
    """
    Genera un PDF con los detalles de una guía de salida específica.
    """
    # Obtener la guía de salida
    guide = get_object_or_404(ExitGuide, pk=guide_id)

    # Crear una respuesta HTTP con tipo de contenido PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="guia_salida_{guide.id}.pdf"'

    # Establecer la orientación horizontal (landscape)
    width, height = landscape(letter)  # Esto invierte la orientación a horizontal

    # Crear el canvas para el PDF
    buffer = canvas.Canvas(response, pagesize=(width, height))

    # Título del documento
    buffer.setFont("Helvetica-Bold", 16)
    buffer.drawString(200, height - 50, f"Guía de Salida #{guide.id}")
    buffer.setFont("Helvetica", 12)
    buffer.drawString(50, height - 80, f"Fecha: {guide.created_at.strftime('%d/%m/%Y')}")
    buffer.drawString(50, height - 100, f"Descripción: {guide.description or 'Sin descripción'}")

    # Preparar los datos para la tabla
    data = [["Código SAP", "Descripción", "Cantidad", "Unidad de Medida", "Categoría"]]
    max_description_length = 0

    # Agregar los ítems de la guía a los datos y calcular el máximo largo de la descripción
    for item in guide.items.all():
        description = item.requirement_order_item.sales_order_item.description
        max_description_length = max(max_description_length, len(description))
        data.append([
            item.requirement_order_item.sales_order_item.sap_code,
            description,
            str(item.quantity),
            item.requirement_order_item.sales_order_item.unit_of_measurement,
            item.requirement_order_item.sales_order_item.category,
        ])

    # Calcular el ancho disponible para la descripción
    available_width = width - 150  # Consideramos un margen de 50 a cada lado para la tabla
    description_col_width = available_width * 0.5  # La descripción ocupará la mitad del ancho disponible

    # Definir los anchos de las columnas
    col_widths = [80, description_col_width, 80, 100, 100]

    # Crear la tabla
    table = Table(data, colWidths=col_widths)
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
