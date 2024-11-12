from django.db import models
from employee.models import Technician
from accounting_order_sales.models import SalesOrder
import os
from datetime import datetime

class TechnicianTask(models.Model):
    verb = models.CharField(max_length=50)
    object = models.CharField(max_length=100)
    measurement = models.CharField(max_length=50)
    time = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.verb} {self.object} ({self.time} {self.measurement})"

    class Meta:
        verbose_name = "Tarea de Técnico"
        verbose_name_plural = "Tareas de Técnicos"

class TechnicianCard(models.Model):
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.technician.first_name} - ({self.date})"
    
    class Meta:
        verbose_name = "Tarjeta de Técnico"
        verbose_name_plural = "Tarjetas de técnicos"


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

class TechnicianCardTask(models.Model):
    technician_card = models.ForeignKey(TechnicianCard, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(TechnicianTask, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_time = models.DecimalField(max_digits=7, decimal_places=2, editable=False)
    saler_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    photo = models.ImageField(upload_to=rename_file, null=True, blank=True)
    status = models.BooleanField(default=False)

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
        
    
