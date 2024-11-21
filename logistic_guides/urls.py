from django.urls import path
from .views import create_exit_guide_view

urlpatterns = [
    # Otras rutas
    path('requirement-order/<int:requirement_order_id>/create-exit-guide/', create_exit_guide_view, name='create_exit_guide'),
]
