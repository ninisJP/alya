from datetime import date, datetime, timedelta
import os
import pandas as pd
from django.db import IntegrityError
from django.db.models import Max

from follow_control_technician.models import TechnicianCard, TechnicianCardTask, TechnicianTask


def get_next_order_for_card_task(technician_card) -> int:
    existing_tasks = TechnicianCardTask.objects.filter(technician_card=technician_card)
    if not existing_tasks.exists():
        return 1
    else:
        current_max = existing_tasks.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1


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

def process_technician_tasks_excel(file):
    try:
        print("Iniciando lectura del archivo Excel...")
        # Cargar el archivo con la primera fila como nombres de columna
        df = pd.read_excel(file, header=0)

        # Imprimir las primeras filas para ver cómo están estructurados los datos
        print("Primeras filas del archivo:", df.head().to_string(index=False))

        if df.shape[1] < 6:  # Ahora hay 6 columnas: Verbo, Objeto, Medida, Tiempo, Routine, Frequency
            print("Archivo no tiene las columnas necesarias.")
            raise ValueError("El archivo debe tener al menos 6 columnas: Verbo, Objeto, Medida, Tiempo, Rutina, Frecuencia")

        print("Archivo leído correctamente. Procesando filas...")

        # Obtener combinaciones únicas existentes en la base de datos
        existing_tasks_set = set(
            TechnicianTask.objects.values_list('verb', 'object', 'measurement', 'time', 'rutine', 'frecuency')
        )

        tasks = []
        errors = []  # Lista para almacenar errores por fila
        for index, row in df.iterrows():
            try:
                verb = row['Verbo']  # Usando el nombre de la columna si lo tienes
                object_ = row['Objeto']
                measurement = row['Medida']
                time = row['Tiempo']
                rutine = row['Rutina']  # Nueva columna
                frecuency = row['Frecuencia']  # Nueva columna

                # Verificar si faltan datos en alguna de las columnas
                if pd.isna(verb) or pd.isna(object_) or pd.isna(measurement) or pd.isna(time) or pd.isna(rutine) or pd.isna(frecuency):
                    raise ValueError(f"Datos incompletos en la fila {index + 1}")

                task_tuple = (verb, object_, measurement, time, rutine, frecuency)
                if task_tuple in existing_tasks_set:
                    print(f"Tarea duplicada en fila {index + 1}. No se guardará.")
                    continue  # Saltar tarea si ya existe

                # Crear la tarea con los nuevos campos
                tasks.append(TechnicianTask(verb=verb, object=object_, measurement=measurement, time=time, rutine=rutine, frecuency=frecuency))
                existing_tasks_set.add(task_tuple)  # Agregar a `existing_tasks_set` para evitar duplicados en la misma carga
            except Exception as row_error:
                errors.append(f"Fila {index + 1}: {str(row_error)}")

        # Guardar todas las tareas nuevas en un solo paso
        if tasks:
            TechnicianTask.objects.bulk_create(tasks)
            print("Todas las tareas nuevas guardadas en la base de datos.")
        else:
            print("No se encontraron tareas nuevas para guardar.")

        # Mostrar errores si los hay
        if errors:
            for error in errors:
                print("Error:", error)
            return False, "Errores en algunas filas. Revísalos en los detalles de la salida."
        return True, None
    except Exception as e:
        print("Error durante el procesamiento del archivo:", str(e))
        return False, str(e)
