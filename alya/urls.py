from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    # Hub
    path('', include('hub.urls')),
    # Accounting - Order
    path('contabilidad-ordenventa/', include('accounting_order_sales.urls')),
    # Follow
    path('tarjeta-control/', include('follow_control_home.urls')),
    path('follow/control/card/', include('follow_control_card.urls')),
    path('follow/control/backlog/', include('follow_control_backlog.urls')),
    path('follow/control/report/', include('follow_control_report.urls')),
    path('follow/control/technician/', include('follow_control_technician.urls')),
    # Employee
    path('employee/', include('employee.urls')),
    path('employee_api/', include('employee_api.urls')),
    path('empleado_portal/', include('employee_portal.urls')),
    # Client
    path('clientes/', include('client.urls')),
    path('clientes/crm/', include('client_crm.urls')),
    # Project
    path('proyectos/', include('project.urls')),
    # Budget
    path('presupuestos/', include('budget.urls')),
    # Requests
    path('pedidos/', include('requests.urls')),
    # DJANGO BROWSER RELOAD
    path("__reload__/", include("django_browser_reload.urls")),
    # LOGISTIC
    path('logistic/inventory/', include('logistic_inventory.urls')),
    path('logistic/inventory/api/', include('logistic_inventory_api.urls')),
    path('logistic/requirements/', include('logistic_requirements.urls')),
    path('logistic/suppliers/', include('logistic_suppliers.urls')),
    path('logistic/api/', include('logistic_api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
