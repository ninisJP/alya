from datetime import timedelta
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
    # Atributos del modelo
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    valuation = models.CharField(max_length=2, default='D')
    total_time = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    efficiency_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Agregar una variable de clase para evitar la recursión
    _is_calculating = False

    def calculate_start_times(self):
        """Recalcular las horas de inicio y fin de todas las tareas asociadas a esta tarjeta."""
        
        if self._is_calculating:  # Evitar recursión infinita
            return
        
        self._is_calculating = True  # Activamos la variable de control
        
        start_time = timedelta(hours=8)  # Iniciar a las 8:00 AM (480 minutos)
        card_task_orders = self.cardtaskorder_set.all().order_by('order')

        for card_task_order in card_task_orders:
            start_hour = (start_time.seconds // 3600) % 24
            start_minute = (start_time.seconds // 60) % 60
            card_task_order.start_time = f'{start_hour:02d}:{start_minute:02d}'

            # Calcular la hora de fin sumando la duración de la tarea al start_time
            task_duration = timedelta(minutes=int(card_task_order.task.task_time))
            end_time = start_time + task_duration

            end_hour = (end_time.seconds // 3600) % 24
            end_minute = (end_time.seconds // 60) % 60
            card_task_order.end_time = f'{end_hour:02d}:{end_minute:02d}'

            card_task_order.save()

            # Actualizar el tiempo de inicio para la siguiente tarea
            start_time = end_time

        self._is_calculating = False  # Restauramos la variable a su estado original

    def update_card_values(self):
        tasks = self.tasks.filter(cardtaskorder__state=True)
        self.total_time = tasks.aggregate(Sum('task_time'))['task_time__sum'] or 0.00
        self.update_efficiency()
        self.save()

    def update_efficiency(self):
        if self.total_time > 0:
            self.efficiency_percentage = (self.total_time / 480) * 100
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
            self.valuation = 'D'

        self.save()

    def __str__(self):
        return f"{self.date} - {self.user.username}"

    class Meta:
        verbose_name = "Tarjeta"
        verbose_name_plural = "Tarjetas"

def get_default_admin():
    return User.objects.get(username='admin')

class Task(models.Model):
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
    cards = models.ManyToManyField('Card', related_name='tasks', through='CardTaskOrder')
    verb = models.CharField(max_length=100, default='')
    object = models.CharField(max_length=100, default='')
    sale_order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, null=True, blank=True)
    measurement = models.CharField(max_length=50, default='minutos')
    task_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    label = models.CharField(max_length=20, null=True, blank=True)
    rutine = models.CharField(max_length=20,choices=TYPE_RUTINE, default='NO RUTINARIA')
    frecuency = models.CharField(max_length=20,choices=TYPE_FRECUENCY, default='UNICA')

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
    executed_at = models.DateTimeField(null=True, blank=True)  # Fecha de ejecución opcional
    start_time = models.TimeField(null=True, blank=True)  # Hora de inicio de la tarea
    end_time = models.TimeField(null=True, blank=True)    # Hora de finalización de la tarea

    class Meta:
        ordering = ['order']
        verbose_name = "Orden de Tarjeta-Tarea"
        verbose_name_plural = "Órdenes de Tarjetas-Tareas"


class TaskExecution(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='executions')
    executed_at = models.DateField(auto_now_add=True)  # Fecha de ejecución
    card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True)  # Tarjeta asociada (opcional)

# Señales para actualizar Card cuando cambie CardTaskOrder
@receiver(post_save, sender=CardTaskOrder)
@receiver(post_delete, sender=CardTaskOrder)
def update_card_on_task_change(sender, instance, **kwargs):
    """Recalcular las horas de las tareas cuando cambien."""
    card = instance.card
    card.calculate_start_times()  # Recalcular las horas de inicio y finalización
    card.update_card_values()  # Recalcular tiempo total y eficiencia
    card.update_valuation()  # Recalcular la valoración

@receiver(post_save, sender=CardTaskOrder)
def log_task_execution(sender, instance, **kwargs):
    if instance.state:  # Si la tarea fue marcada como completada
        TaskExecution.objects.create(task=instance.task, card=instance.card)
