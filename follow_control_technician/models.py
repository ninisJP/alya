from django.db import models
from employee.models import Technician

class TechnicianTask(models.Model):
    object = models.CharField(max_length=100)
    verb = models.CharField(max_length=50)
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
    saler_order = models.CharField(max_length=50)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.task.verb} {self.task.object} (Order: {self.order})"

    class Meta:
        ordering = ['order']