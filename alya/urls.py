"""
URL configuration for alya project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    # Hub
    path('', include('hub.urls')),
    # Accounting - Order
    path('accounting_order_sales/', include('accounting_order_sales.urls')),
    # Follow
    path('follow/control/', include('follow_control_home.urls')),
    path('follow/control/card/', include('follow_control_card.urls')),
    path('follow/control/backlog/', include('follow_control_backlog.urls')),
    path('follow/control/report/', include('follow_control_report.urls')),
    path('follow/control/technician/', include('follow_control_technician.urls')),
    # Employee
    path('employee/', include('employee.urls')),
    path('employee_api/', include('employee_api.urls')),
    # Client
    path('clientes/', include('client.urls')),
    # Project
    path('project/', include('project.urls')),
    # DJANGO BROWSER RELOAD
    path("__reload__/", include("django_browser_reload.urls")),

]
