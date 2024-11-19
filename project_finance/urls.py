from django.urls import path
from .views import dashboard, accounts_payable_detail

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
]

htmxpatterns = [
    path('dashboard/accounts_payable_detail/', accounts_payable_detail, name='accounts_payable_detail')
]



urlpatterns = urlpatterns + htmxpatterns
