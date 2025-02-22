# See LICENSE file for copyright and license details.
"""
Requiments order views
"""
from datetime import datetime, timedelta
# import calendar

from django.shortcuts import render
from django.urls import reverse
# from django.utils.timezone import now
# from collections import defaultdict

from follow_control_card.models import Card
from . import utils


def HomeCC(request):
    """
    Main task orden view.
    """

    # Obtener el mes y año actual
    today = datetime.today()
    month = today.month
    year = today.year

    # Filtrar tarjetas del usuario actual y del mes actual
    cards = Card.objects.filter(user=request.user, date__year=year, date__month=month)

    # Crear eventos para el calendario, basados en las tareas de cada tarjeta en el mismo día
    events = []
    card_urls = {}
    for card in cards:
        tasks = card.tasks.order_by('cardtaskorder__order')

        # Generar la URL de cada Card y guardarla en el diccionario usando la fecha como clave
        card_url = reverse('daily_card', args=[card.id])
        card_urls[card.date.strftime("%Y-%m-%d")] = card_url

        # Generar eventos para cada tarea
        start_time = datetime.combine(card.date, datetime.min.time()) + timedelta(hours=8)
        for task in tasks:
            task_duration_hours = float(task.task_time or 0) / 60  # Convertir minutos a horas
            end_time = start_time + timedelta(hours=task_duration_hours)

            # Obtener el código SAP de la orden de venta si está disponible
            sap_code = task.sale_order.sapcode if task.sale_order else "Sin código SAP"

            # Cambiar 'title' para incluir `sapcode` directamente en el nombre del evento
            events.append({
                'title': f"{task.verb} {task.object} - SAP: {sap_code}",  # Mostrar `sapcode` en el título
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'url': card_url,
                'description': f"{task.verb} {task.object} - SAP: {sap_code}"
            })
            start_time = end_time

    return render(request, 'home_cc.html', {'events': events, 'card_urls': card_urls})


def export_to_excel(request):
    """
    Export to excel all task by date in a month
    """

    wb, ws = utils.card_excel_prepare(request.user)
    ws = utils.card_excel_header(ws)
    response = utils.card_excel_item(wb, ws, request.user)

    return response
