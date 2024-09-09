from django.db import models
from employee.models import Technician
from accounting_order_sales.models import SalesOrder

class TechnicianTask(models.Model):
    verb = models.CharField(max_length=50)
    object = models.CharField(max_length=100)
    measurement = models.CharField(max_length=50)
    time = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.verb} {self.object} ({self.time} {self.measurement})"


class TechnicianCard(models.Model):
    technician = models.ForeignKey(Technician, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.technician.name} - ({self.date})"


class TechnicianCardTask(models.Model):
    technician_card = models.ForeignKey(TechnicianCard, on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey(TechnicianTask, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_time = models.DecimalField(max_digits=7, decimal_places=2, editable=False)
    saler_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    
    # Campo de foto que no se incluirá en el formulario
    photo = models.ImageField(upload_to='technician_tasks_photos/', null=True, blank=True)

    # Campo de estado
    STATUS_CHOICES = [
        ('not_done', 'No Hecha'),
        ('incomplete', 'Incompleta'),
        ('completed', 'Completada'),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='not_done')

    def __str__(self):
        return f"{self.task.verb} {self.task.object} (Order: {self.order})"

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        # Calcular total_time como time * quantity
        self.total_time = self.task.time * self.quantity
        super().save(*args, **kwargs)
