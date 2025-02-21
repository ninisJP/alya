# See LICENSE file for copyright and license details.
"""
Follow control views
"""
from django.urls import path

from . import views

urlpatterns = [
     path('', views.HomeCC, name='follow_control_home'),
     path(
         'export2excel',
         views.export_to_excel,
          name='follow_control_export2excel'
     ),
]
