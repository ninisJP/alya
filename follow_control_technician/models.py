from django.db import models
from employee.models import Technician
from accounting_order_sales.models import SalesOrder
import os
from datetime import datetime, time

class TechnicianTaskGroup(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Grupo de Tareas de Técnico"
        verbose_name_plural = "Grupos de Tareas de Técnicos"

def rename_file(instance, filename):
    # Extraer información relevante del modelo TechnicianCardTask
    technician_name = instance.technician_card.technician.first_name.replace(' ', '_')
    task_description = instance.task.verb.replace(' ', '_')
    order = instance.order
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H-%M-%S")

    # Generar el nuevo nombre del archivo
    base_name, extension = os.path.splitext(filename)
    new_filename = f"{technician_name}_{task_description}_order{order}_{current_date}_{current_time}{extension}"

    return os.path.join('technician_tasks_photos', new_filename)

class TechnicianTask(models.Model):
    TYPE_RUTINE = [
        ('NO RUTINARIA', 'NO RUTINARIA'),
        ('RUTINARIA', 'RUTINARIA'),
    ]
    TYPE_FRECUENCY = [
        ('UNICA', 'UNICA'),
        ('DIARIA', 'DIARIA'),
        ('INTERDIARIA', 'INTERDIARIA'),
        ('SEMANAL', 'SEMANAL'),
        ('MENSUAL', 'MENSUAL'),
    ]
    verb = models.CharField(max_length=150)
    object = models.CharField(max_length=350)
    measurement = models.CharField(max_length=50)
    time = models.DecimalField(max_digits=5, decimal_places=2)
    rutine = models.CharField(max_length=20, choices=TYPE_RUTINE, default='NO RUTINARIA')
    frecuency = models.CharField(max_length=20, choices=TYPE_FRECUENCY, default='UNICA' )

    def __str__(self):
        return f"{self.verb} {self.object} ({self.time} {self.measurement} {self.rutine} {self.frecuency})"

    class Meta:
        verbose_name = "Tarea de Técnico"
        verbose_name_plural = "Tareas de Técnicos"
        unique_together = ('verb', 'object', 'measurement', 'time')  # Aquí va la restricción de `unique_together`


class TechnicianCard(models.Model):
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    date = models.DateField()
    start_hour = models.TimeField(default=time(8, 0))  # Hora de inicio por defecto a las 8:00 a.m.

    def __str__(self):
        return f"{self.technician.first_name} - ({self.date})"

    class Meta:
        verbose_name = "Tarjeta de Técnico"
        verbose_name_plural = "Tarjetas de técnicos"

class TechnicianCardTask(models.Model):
    technician_card = models.ForeignKey(TechnicianCard, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(TechnicianTask, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_time = models.DecimalField(max_digits=7, decimal_places=2, editable=False)
    saler_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, null=True, blank=True)  # Permitir nulos
    order = models.PositiveIntegerField()
    photo = models.ImageField(upload_to=rename_file, null=True, blank=True)
    status = models.BooleanField(default=False)
    task_group = models.ForeignKey(TechnicianTaskGroup, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return f"{self.task.verb} {self.task.object} (Order: {self.order})"

    class Meta:
        ordering = ['order']
        verbose_name = "Tarjeta de Tarea de Técnico"
        verbose_name_plural = "Tarjetas de Tareas de Técnicos"


    def save(self, *args, **kwargs):
        # Calcular total_time como time * quantity
        self.total_time = self.task.time * self.quantity
        super().save(*args, **kwargs)


class TechnicianTaskGroupItem(models.Model):
    task_group = models.ForeignKey(
        TechnicianTaskGroup, on_delete=models.CASCADE, related_name="group_items"
    )
    task = models.ForeignKey(TechnicianTask, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Cantidad específica para la tarea en el grupo
    saler_order = models.ForeignKey(
        SalesOrder, on_delete=models.CASCADE, null=True, blank=True
    )  # Orden de venta puede ser opcional
    order = models.PositiveIntegerField(default=1)  # Orden de la tarea dentro del grupo

    def __str__(self):
        return f"{self.task} en {self.task_group} (Cantidad: {self.quantity}, Orden: {self.order})"

    class Meta:
        verbose_name = "Elemento del Grupo de Tareas"
        verbose_name_plural = "Elementos del Grupo de Tareas"
        ordering = ['order']  # Siempre ordena por el campo `order` por defecto

