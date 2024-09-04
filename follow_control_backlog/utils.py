from datetime import datetime
from datetime import datetime, timedelta

import calendar

def get_current_year_month():
    now = datetime.now()
    return now.year, now.month

def get_current_month_dates():
    today = datetime.today()
    current_year = today.year
    current_month = today.month

    nombre_mes = calendar.month_name[current_month]
    _, days_in_month = calendar.monthrange(current_year, current_month)
    days = list(range(1, days_in_month + 1))

    days = [day for day in days if (datetime(current_year, current_month, day).weekday() + 1) % 7 != 0]

    primer_dia_semana = datetime(current_year, current_month, 1).weekday()
    empty_days = list(range(primer_dia_semana)) if primer_dia_semana != 6 else list(range(6))

    start_of_month = today.replace(day=1)
    end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
                    if start_of_month.month != 12 else start_of_month.replace(year=start_of_month.year + 1, month=1, day=1)) - timedelta(days=1)

    days_without_sundays = [start_of_month + timedelta(days=i) for i in range((end_of_month - start_of_month).days + 1)
                            if (start_of_month + timedelta(days=i)).weekday() != 6]

    return {
        'current_year': current_year,
        'current_month': current_month,
        'nombre_mes': nombre_mes,
        'days_in_month': days,
        'empty_days': empty_days,
        'start_of_month': start_of_month,
        'end_of_month': end_of_month,
        'days_without_sundays': days_without_sundays
    }

def get_month_dates(year, month):
    current_year = year
    current_month = month

    nombre_mes = calendar.month_name[current_month]
    _, days_in_month = calendar.monthrange(current_year, current_month)
    days = list(range(1, days_in_month + 1))

    # Eliminar los domingos
    days = [day for day in days if (datetime(current_year, current_month, day).weekday() + 1) % 7 != 0]

    # Calcular los días vacíos al inicio del mes
    primer_dia_semana = datetime(current_year, current_month, 1).weekday()
    empty_days = list(range(primer_dia_semana)) if primer_dia_semana != 6 else list(range(6))

    start_of_month = datetime(current_year, current_month, 1)
    end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
                    if start_of_month.month != 12 else start_of_month.replace(year=start_of_month.year + 1, month=1, day=1)) - timedelta(days=1)

    days_without_sundays = [start_of_month + timedelta(days=i) for i in range((end_of_month - start_of_month).days + 1)
                            if (start_of_month + timedelta(days=i)).weekday() != 6]

    months = [
        {"number": 1, "name": "Enero"},
        {"number": 2, "name": "Febrero"},
        {"number": 3, "name": "Marzo"},
        {"number": 4, "name": "Abril"},
        {"number": 5, "name": "Mayo"},
        {"number": 6, "name": "Junio"},
        {"number": 7, "name": "Julio"},
        {"number": 8, "name": "Agosto"},
        {"number": 9, "name": "Septiembre"},
        {"number": 10, "name": "Octubre"},
        {"number": 11, "name": "Noviembre"},
        {"number": 12, "name": "Diciembre"},
    ]
    years = list(range(2020, 2031))

    return {
        'current_year': current_year,
        'current_month': current_month,
        'nombre_mes': nombre_mes,
        'days_in_month': days,
        'empty_days': empty_days,
        'start_of_month': start_of_month,
        'end_of_month': end_of_month,
        'days_without_sundays': days_without_sundays,
        'months': months,
        'years': years,
    }
