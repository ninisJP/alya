# See LICENSE file for copyright and license details.
"""
Models to Task Note
"""
from django.db import models


class TaskNote(models.Model):
    """
    TaskNote model
    model use to make complaints within tha system

    Parameters
    ----------
    title: str
        Title of the task
    description : str
        Description of the task
    urgency_level : int, default: medium
        Urgency level of the task
    created_date : date
        Date of the task
    waiting_time : int
        Time waiting
    due_date : date
        Due date of the task
    status : str, default: pending
        Status of the task
    rejection_reason : str
        Reason for rejection of the task
    Choices
    -------
    STATUS_CHOICES : List of tuples, default: pending
        determines the position of the requested requirement,
        changes are made in the admin panel
    """

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("completed", "Listo"),
        ("rejected", "Rechazado"),
    ]

    title = models.CharField(
        max_length=100,
        help_text="Título breve de la tarea")
    description = models.TextField(
        blank=True,
        help_text="Descripción detallada de la tarea")
    urgency_level = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        help_text="Nivel de urgencia de la tarea"
    )
    created_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha en la que se creó la tarea"
    )
    waiting_time = models.DurationField(
        blank=True,
        null=True,
        help_text="Tiempo esperando"
    )
    due_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Fecha límite para completar la tarea"
    )
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
        return str(self.description)
