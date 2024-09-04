from django.urls import path
from .views import valuations_view

urlpatterns = [
    path('valuations/<int:year>/<int:month>/', valuations_view, name='valuations'),
]
