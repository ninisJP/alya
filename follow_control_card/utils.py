import pandas as pd

from django.db.models import Max
from datetime import date, timedelta
from follow_control_card.models import Card, CardTaskOrder, Task


def get_max_order(card) -> int:
    existing_tasks = CardTaskOrder.objects.filter(card=card)
    if not existing_tasks.exists():
        return 1
    else:
        current_max = existing_tasks.aggregate(max_order=Max('order'))['max_order']
        return current_max + 1


def create_monthly_cards_for_user(user):
    today = date.today()
    start_of_month = today.replace(day=1)
    next_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1)
                  if start_of_month.month != 12 else start_of_month.replace(year=start_of_month.year + 1, month=1, day=1))
    days_in_month = (next_month - start_of_month).days

    for day in range(days_in_month):
        card_date = start_of_month + timedelta(days=day)

        # Verificar antes de crear
        if not Card.objects.filter(user=user, date=card_date).exists():
            Card.objects.create(user=user, date=card_date)

from django.contrib.auth.models import User

def process_tasks_excel(file, sale_order):
    try:
        print("Iniciando lectura del archivo Excel...")
        df = pd.read_excel(file, header=0)

        if df.shape[1] < 6:
            print("Archivo no tiene las columnas necesarias.")
            raise ValueError("El archivo debe tener al menos 6 columnas: Verbo, Objeto, Medida, Tiempo, Rutina, Frecuencia, Usuario")

        print("Archivo leído correctamente. Procesando filas...")

        tasks = []
        errors = []  # Lista para almacenar errores por fila
        for index, row in df.iterrows():
            try:
                verb = row['Verbo']
                object_ = row['Objeto']
                measurement = row['Medida']
                time = row['Tiempo']
                rutine = row['Rutina']
                frecuency = row['Frecuencia']
                user = row['Usuario']

                if pd.isna(verb) or pd.isna(object_) or pd.isna(measurement) or pd.isna(time) or pd.isna(rutine) or pd.isna(frecuency) or pd.isna(user):
                    raise ValueError(f"Datos incompletos en la fila {index + 1}")

                # Buscar el usuario en la base de datos
                try:
                    user_instance = User.objects.get(username=user)  # O usa otro campo si no es 'username'
                except User.DoesNotExist:
                    raise ValueError(f"El usuario '{user}' no existe en la base de datos.")

                # Crear la tarea con la sale_order seleccionada
                task = Task(
                    verb=verb,
                    object=object_,
                    measurement=measurement,
                    task_time=time,
                    rutine=rutine,
                    frecuency=frecuency,
                    sale_order=sale_order,  # Asocia la tarea con la orden de venta seleccionada
                    user=user_instance  # Asigna la instancia de usuario
                )
                tasks.append(task)
            except Exception as row_error:
                errors.append(f"Fila {index + 1}: {str(row_error)}")

        # Guardar todas las tareas nuevas en un solo paso
        if tasks:
            Task.objects.bulk_create(tasks)
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
