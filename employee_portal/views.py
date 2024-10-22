from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .forms import EditProfileForm 

@login_required
def index_portal(request):
    user = User.objects.all()
    return render(request, 'index_portal.html', {'users': user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('profile') 
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, 'edit_portal.html', {'form': form})


@login_required
def confirm_password_change(request):
    return render(request, 'confirm_password_change.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'change_password.html', {'form': form})

from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounting_order_sales.models import PurchaseOrderItem 
from logistic_suppliers.models import Suppliers
from django.utils.timezone import localdate

@login_required
def my_renditions(request):
    # Obtener el usuario actual
    user = request.user

    # Verificar si el usuario es técnico o supervisor
    if hasattr(user, 'technician'):
        dni = user.technician.dni
    elif hasattr(user, 'supervisors'):
        dni = user.supervisors.dni
    else:
        # Si el usuario no tiene un perfil de técnico ni de supervisor, no tiene acceso a esta vista
        return render(request, 'my_renditions/error.html', {'message': 'No tiene un perfil válido para acceder a las rendiciones.'})

    # Fechas de filtro opcionales
    today = localdate()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filtrar los PurchaseOrderItems asignados al proveedor cuyo DNI coincide con el del usuario
    if not start_date and not end_date:
        items = PurchaseOrderItem.objects.filter(
            supplier__document=dni,
            purchaseorder__scheduled_date=today
        ).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')
    else:
        if not end_date:
            end_date = today

        items = PurchaseOrderItem.objects.filter(
            supplier__document=dni,
            purchaseorder__scheduled_date__range=[start_date, end_date]
        ).select_related('purchaseorder', 'sales_order_item__salesorder', 'supplier')

    # Calcular el total restante para cada ítem
    for item in items:
        total_renditions = item.renditions.aggregate(total=Sum('amount'))['total'] or 0
        item.total_remaining = item.price_total - total_renditions if item.price_total else 0

    context = {
        'items': items,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'my_renditions/my_renditions.html', context)
