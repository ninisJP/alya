from django.urls import path
from .views import create_exit_guide_view, list_requirement_order_guides, export_exit_guide_pdf

urlpatterns = [
    # Otras rutas
    path('requirement-order/<int:requirement_order_id>/create-exit-guide/', create_exit_guide_view, name='create_exit_guide'),
    path('requirement-order/<int:requirement_order_id>/guides/', list_requirement_order_guides, name='list_requirement_order_guides'),
    path('guides/export-pdf/<int:guide_id>/', export_exit_guide_pdf, name='export_exit_guide_pdf'),


]
