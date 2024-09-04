from django.db import models

class Technician(models.Model):
    name = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rank = models.CharField(max_length=50)
    technician_class = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} {self.lastname} - {self.rank}"

    class Meta:
        verbose_name = "Technician"
        verbose_name_plural = "Technicians"
        
class TechnicianTask(models.Model):
    object = models.CharField(max_length=100)
    verb = models.CharField(max_length=50)
    measurement = models.CharField(max_length=50)
    time = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.verb} {self.object} ({self.time} {self.measurement})"

    class Meta:
        verbose_name = "Technician Task"
        verbose_name_plural = "Technician Tasks"

class TechnicianCard(models.Model):
    technician = models.ForeignKey('Technician', on_delete=models.CASCADE)
    station = models.CharField(max_length=50, default='Taller AQP')
    date = models.DateField()

    def __str__(self):
        return f"{self.technician.name} - {self.station.name} ({self.date})"

    class Meta:
        verbose_name = "Technician Card"
        verbose_name_plural = "Technician Cards"
        unique_together = ('technician', 'station', 'date')

class TechnicianCardTask(models.Model):
    technician_card = models.ForeignKey('TechnicianCard', on_delete=models.CASCADE, related_name='tasks')
    task = models.ForeignKey('TechnicianTask', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.task.verb} {self.task.object} (Order: {self.order})"

    class Meta:
        verbose_name = "Technician Card Task"
        verbose_name_plural = "Technician Card Tasks"
        ordering = ['order']