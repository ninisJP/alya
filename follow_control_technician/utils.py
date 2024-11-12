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
    
import pandas as pd
from .models import TechnicianTask
from django.db import IntegrityError

def process_technician_tasks_excel(file):
    try:
        print("Iniciando lectura del archivo Excel...")
        df = pd.read_excel(file, header=None)  # Especifica que no hay cabecera

        # Imprimir las primeras filas para ver cómo están estructurados los datos
        print("Primeras filas del archivo:", df.head().to_string(index=False))

        # Validar que el archivo tiene al menos 4 columnas
        if df.shape[1] < 4:
            print("Archivo no tiene las columnas necesarias.")
            raise ValueError("El archivo debe tener al menos 4 columnas: Verbo, Objeto, Medida, Tiempo")

        print("Archivo leído correctamente. Procesando filas...")

        # Obtener las combinaciones de `verb`, `object`, `measurement`, `time` de tareas existentes
        existing_tasks_set = set(
            TechnicianTask.objects.values_list('verb', 'object', 'measurement', 'time')
        )

        tasks = []
        for index, row in df.iterrows():
            verb = row[0]
            object_ = row[1]
            measurement = row[2]
            time = row[3]

            # Validaciones de celdas vacías
            if pd.isna(verb) or pd.isna(object_) or pd.isna(measurement) or pd.isna(time):
                print(f"Fila {index + 1} tiene datos incompletos. Verbo: {verb}, Objeto: {object_}, Medida: {measurement}, Tiempo: {time}")
                raise ValueError(f"La fila {index + 1} en el archivo tiene datos incompletos. Por favor revisa el archivo.")

            # Verificar si la combinación ya existe
            task_tuple = (verb, object_, measurement, time)
            if task_tuple in existing_tasks_set:
                continue  # Saltar esta tarea si ya existe

            # Agrega la tarea a la lista de tareas nuevas
            tasks.append(TechnicianTask(verb=verb, object=object_, measurement=measurement, time=time))

        # Guardar todas las tareas nuevas
        if tasks:
            TechnicianTask.objects.bulk_create(tasks)
            print("Todas las tareas nuevas guardadas en la base de datos.")
        else:
            print("No se encontraron tareas nuevas para guardar.")
        return True, None
    except Exception as e:
        print("Error durante el procesamiento del archivo:", str(e))
        return False, str(e)


