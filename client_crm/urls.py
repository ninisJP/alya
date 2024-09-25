from django.urls import path
from .views import opportunity, index_contract, edit_contract,delete_contract

urlpatterns = [
    path('contrato/', index_contract, name='index_contract'),
    path('contracts/edit/<int:contract_id>/', edit_contract, name='edit_contract'),
    path('contracts/delete/<int:contract_id>/', delete_contract, name='delete_contract'),
    path('oportunidad/', opportunity, name='opportunity'),
]
