from rest_framework import serializers
from django.contrib.auth.models import User
from follow_control_technician.models import TechnicianCard, TechnicianCardTask

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        
class TechnicianCardTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianCardTask
        fields = ['id', 'task', 'quantity', 'total_time', 'saler_order', 'order', 'status']

class TechnicianCardSerializer(serializers.ModelSerializer):
    tasks = TechnicianCardTaskSerializer(many=True, read_only=True)

    class Meta:
        model = TechnicianCard
        fields = ['id', 'date', 'tasks']