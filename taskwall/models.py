from django.db import models

class TaskNote(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("completed", "Listo"),
        ("rejected", "Rechazado"),
    ]

    title = models.CharField(max_length=100, help_text="Título breve de la tarea")
    description = models.TextField(blank=True, help_text="Descripción detallada de la tarea")
    urgency_level = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        help_text="Nivel de urgencia de la tarea"
    )
    created_date = models.DateTimeField(auto_now_add=True, help_text="Fecha en la que se creó la tarea")
    waiting_time = models.DurationField(blank=True, null=True, help_text="Tiempo esperando")
    due_date = models.DateTimeField(blank=True, null=True, help_text="Fecha límite para completar la tarea")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Estado de la tarea"
    )
    rejection_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Razón de rechazo de la tarea, si aplica"
    )

    def save(self, *args, **kwargs):
        # Si el estado no es "Rechazado", limpiar el campo `rejection_reason`
        if self.status != "rejected":
            self.rejection_reason = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
