from datetime import date, timedelta
from .models import TechnicianCard


def informe_tarjetas_del_mes(mes, anio):
    primer_dia_mes = date(anio, mes, 1)
    ultimo_dia_mes = primer_dia_mes + timedelta(days=28) + timedelta(days=4)
    ultimo_dia_mes = ultimo_dia_mes - timedelta(days=ultimo_dia_mes.day)

    tarjetas_del_mes = TechnicianCard.objects.filter(
        date__range=(primer_dia_mes, ultimo_dia_mes)
    ).order_by('technician', 'date')

    print(f"Tarjetas encontradas: {tarjetas_del_mes.count()}")

    informe = {}
    for tarjeta in tarjetas_del_mes:
        tecnico_id = tarjeta.technician.id
        if tecnico_id not in informe:
            informe[tecnico_id] = {
                'technician': f"{tarjeta.technician.name} {tarjeta.technician.lastname}",
                'dias_con_tarjeta': set(),
                'dias_sin_tarjeta': set(range(1, (ultimo_dia_mes - primer_dia_mes).days + 2))
            }
        informe[tecnico_id]['dias_con_tarjeta'].add(tarjeta.date.day)
        informe[tecnico_id]['dias_sin_tarjeta'].discard(tarjeta.date.day)

    for tecnico_id, datos in informe.items():
        datos['dias_con_tarjeta'] = sorted(list(datos['dias_con_tarjeta']))
        datos['dias_sin_tarjeta'] = sorted(list(datos['dias_sin_tarjeta']))

    print(f"Informe: {informe}")

    return {
        'mes': primer_dia_mes.strftime('%B'),
        'anio': primer_dia_mes.year,
        'informe_por_tecnico': informe
    }
