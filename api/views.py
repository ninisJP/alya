from django.contrib.auth.models import User
from rest_framework import  viewsets, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from employee.models import Supervisor,Technician
from .serializers import *

class TechnicianViewSet(viewsets.ModelViewSet):
    queryset = Technician.objects.all()
    serializer_class = TechnicianSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny]  
        else:
            self.permission_classes = [IsAuthenticated]  
        return super().get_permissions()

class SupervisorViewSet(viewsets.ModelViewSet):
    queryset = Supervisor.objects.all()
    serializer_class = SupervisorSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny]  
        else:
            self.permission_classes = [IsAuthenticated]  
        return super().get_permissions()
    

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]  
        return super().get_permissions()
