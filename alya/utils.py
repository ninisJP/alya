import re
from django.core.mail import send_mail
from django.conf import settings

# Example: search_model(Brand.objects.all(), 'name', form.cleaned_data['name'])
# Return status, list_model
def search_model(model_all, column, name, accept_all=False):
    # Minimal word's length is 4
    if not accept_all :
        if len(name) < 4 :
            return -1, {}

    model_list = list(model_all.values())

    regex_str = str(name)

    list_find = []
    for element in model_list:
        match = re.findall(regex_str, str(element[column]), re.IGNORECASE)
        match = ''.join(match)
        if len(match):
            list_find.append(element)

    # Get model id
    list_id = []
    for item in list_find :
        list_id.append(item['id'])

    # Get model
    model_list = model_all.filter(pk__in=list_id)

    if len(model_list) == 0:
        return -2, model_list
    return 0, model_list

def send_order_notification(requirement_order, user, extra_recipients=None):
    """
    Envía un correo electrónico notificando que se ha creado un nuevo pedido.
    
    Parameters:
    - requirement_order: La orden de requerimiento creada.
    - user: El usuario que creó la orden.
    - extra_recipients: Lista opcional de correos electrónicos adicionales.
    """
    # Asunto y mensaje predefinido
    subject = f"Nuevo Pedido Creado: {requirement_order.id} por {user.username}"
    message = (
        f"Hola,\n\n"
        f"Se ha creado un nuevo pedido con el ID {requirement_order.id} asociado a la orden de venta {requirement_order.sales_order.id}.\n"
        f"El pedido ha sido creado por {user.username} y está pendiente de aprobación.\n\n"
        f"Detalles del Pedido:\n"
        f"- Orden de Venta: {requirement_order.sales_order}\n"
        #f"- Usuario: {user.get_full_name()} ({user.email})\n\n"
        f"Saludos,\n"
        f"Equipo de Gestión"
    )

    # Lista de destinatarios
    recipient_list = [user.email]  # Correo del usuario
    if extra_recipients:
        recipient_list.extend(extra_recipients)  # Añade correos adicionales si los hay

    # Enviar el correo
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

def send_state_change_email(requirement_order):
    """
    Envía un correo notificando si un pedido ha sido aprobado o rechazado.
    """
    subject = f"Pedido {requirement_order.order_number} {requirement_order.state}"
    if requirement_order.state == 'APROBADO':
        message = f"Tu pedido {requirement_order.order_number} ha sido aprobado. Para más información, consulta el sistema JP o tu aplicativo."
    elif requirement_order.state == 'RECHAZADO':
        message = f"Tu pedido {requirement_order.order_number} ha sido rechazado. Para más información, consulta el sistema JP o tu aplicativo."

    # Lista de destinatarios
    recipient_list = [requirement_order.user.email]
    # Agrega correos adicionales, por ejemplo, de un encargado
    encargado_email = '71729475@certus.edu.pe'  # Cambia esto al correo real
    recipient_list.append(encargado_email)

    # Enviar el correo
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False,
    )

