from django.urls import path
from .views import contract, opportunity

urlpatterns = [
    path('contrato/', contract, name='contract'),
    path('oportunidad/', opportunity, name='opportunity'),
]
