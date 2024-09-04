from django.db import models
from django.contrib.auth.models import User


class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    valuation = models.CharField(max_length=1, default='D')
    total_time = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def update_card_values(self):
        tasks = self.tasks.all()
        self.total_time = tasks.aggregate(models.Sum('task_time'))['task_time__sum'] or 0.00
        self.save()

    def update_valuation(self):
        total_tasks = self.tasks.count()
        completed_tasks = self.tasks.filter(cardstasksorder__state=True).count()
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            if completion_rate == 100:
                self.valuation = 'SS'
            elif completion_rate >= 90:
                self.valuation = 'S'
            elif completion_rate >= 85:
                self.valuation = 'A+'
            elif completion_rate >= 80:
                self.valuation = 'A'
            elif completion_rate >= 75:
                self.valuation = 'A-'
            elif completion_rate >= 70:
                self.valuation = 'B+'
            elif completion_rate >= 65:
                self.valuation = 'B'
            elif completion_rate >= 60:
                self.valuation = 'B-'
            elif completion_rate >= 55:
                self.valuation = 'C+'
            elif completion_rate >= 50:
                self.valuation = 'C'
            elif completion_rate >= 45:
                self.valuation = 'C-'
            elif completion_rate >= 40:
                self.valuation = 'D+'
            else:
                self.valuation = 'D'
        else:
            self.valuation = 'D'  # Si no hay tareas, se considera la peor calificación
        self.save()


    def __str__(self):
        return f"{self.date} - {self.user.username}"

class Task(models.Model):
    cards = models.ManyToManyField('Card', related_name='tasks', through='CardTaskOrder')
    verb = models.CharField(max_length=100, default='')
    object = models.CharField(max_length=100, default='')
    orden_venta = models.CharField(max_length=200, db_index=True, default='')
    client = models.CharField(max_length=200, default='')
    measurement = models.CharField(max_length=50, default='minutos')
    task_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return self.verb

class CardTaskOrder(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    state = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
