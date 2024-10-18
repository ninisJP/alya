# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RequirementOrder
from alya.utils import send_order_notification

@receiver(post_save, sender=RequirementOrder)
def notify_on_requirement_order_creation(sender, instance, created, **kwargs):
    """
    Envía una notificación por correo cuando se crea una nueva orden de requerimiento.
    """
    if created:  # Solo envía el correo cuando se crea una nueva instancia
        user = instance.user
        # Destinatarios adicionales (por ejemplo, encargados)
        extra_recipients = ['71729475@certus.edu.pe']
        # Llama a la función de utilidad para enviar el correo
        send_order_notification(instance, user, extra_recipients)
