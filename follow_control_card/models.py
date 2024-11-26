from django.db import models
from django.contrib.auth.models import User
from accounting_order_sales.models import SalesOrder
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Umbrales para las calificaciones
CALIFICATION_THRESHOLDS = {
    'SS': 100,
    'S': 90,
    'A+': 85,
    'A': 80,
    'A-': 75,
    'B+': 70,
    'B': 65,
    'B-': 60,
    'C+': 55,
    'C': 50,
    'C-': 45,
    'D+': 40,
    'D': 0
}

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    valuation = models.CharField(max_length=2, default='D')  # Máximo 2 caracteres (ej. "SS")
    total_time = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    efficiency_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def update_card_values(self):
        # Solo sumar el tiempo de las tareas completadas
        tasks = self.tasks.filter(cardtaskorder__state=True)  # Solo tareas completadas
        self.total_time = tasks.aggregate(Sum('task_time'))['task_time__sum'] or 0.00
        self.update_efficiency()
        self.save()

    def update_efficiency(self):
        # Solo calculamos la eficiencia con el tiempo de las tareas completadas
        if self.total_time > 0:
            self.efficiency_percentage = (self.total_time / 480) * 100  # Basado en 480 minutos
        else:
            self.efficiency_percentage = 0.00
        self.save()

    def update_valuation(self):
        total_tasks = self.tasks.count()
        completed_tasks = self.tasks.filter(cardtaskorder__state=True).count()

        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            for grade, threshold in CALIFICATION_THRESHOLDS.items():
                if completion_rate >= threshold:
                    self.valuation = grade
                    break
        else:
            self.valuation = 'D'  # Sin tareas = peor calificación

        self.save()

    def __str__(self):
        return f"{self.date} - {self.user.username}"

    class Meta:
        verbose_name = "Tarjeta"
        verbose_name_plural = "Tarjetas"


class Task(models.Model):
    cards = models.ManyToManyField('Card', related_name='tasks', through='CardTaskOrder')
    verb = models.CharField(max_length=100, default='')
    object = models.CharField(max_length=100, default='')
    sale_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE)
    measurement = models.CharField(max_length=50, default='minutos')
    task_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return self.verb

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"


class CardTaskOrder(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    order = models.PositiveSmallIntegerField()
    state = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    class Meta:
        verbose_name = "Orden de Tarjeta-Tarea"
        verbose_name_plural = "Ordenes de Tarjetas-Tareas"


# Señales para actualizar Card cuando cambie CardTaskOrder
@receiver(post_save, sender=CardTaskOrder)
@receiver(post_delete, sender=CardTaskOrder)
def update_card_on_task_change(sender, instance, **kwargs):
    # Obtiene la tarjeta asociada
    card = instance.card
    # Recalcula los valores de la tarjeta (tiempo total y eficiencia)
    card.update_card_values()
    card.update_valuation()
