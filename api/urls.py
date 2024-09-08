from django.urls import path, include
from rest_framework import routers
from django.contrib.auth.decorators import login_not_required
from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# API list urls
urlpatterns = [
    path('', include(router.urls)),
    path('api/', include('rest_framework.urls', namespace='rest_framework')),
    path('v1/list/', login_not_required(UserViewSet.as_view({'get': 'list'})), name='user-list'),
    path('v1/list/supervisor/', login_not_required(SupervisorViewSet.as_view({'get': 'list'})), name='user-list'),
    path('v1/list/technician/', login_not_required(TechnicianViewSet.as_view({'get': 'list'})), name='user-list'),

]


