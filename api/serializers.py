from django.contrib.auth.models import User
from employee.models import Supervisor,Technician
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ['id', 'user', 'first_name', 'last_name', 'position', 'status', 'email']
        
class TechnicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Technician
        fields = ['id', 'user', 'first_name', 'last_name', 'position', 'status', 'email']
