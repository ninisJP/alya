from rest_framework import serializers
from django.contrib.auth.models import User
from follow_control_technician.models import TechnicianCard, TechnicianCardTask, TechnicianTask

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TechnicianCardTaskSimplifiedSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    # add photo 
    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = TechnicianCardTask
        fields = ['id', 'description','photo_url']

    def get_description(self, obj):
        return (
            f"{obj.task.verb} {obj.task.object} ({obj.task.time} {obj.task.measurement}) * "
            f"{obj.quantity} - {obj.total_time} MIN - {obj.saler_order.detail} - ORDEN {obj.order}"
        )
    def get_photo_url(self, obj):
        if obj.photo and 'request' in self.context:
            return self.context['request'].build_absolute_uri(obj.photo.url)
        return None

class TechnicianCardSerializer(serializers.ModelSerializer):
    tasks = TechnicianCardTaskSimplifiedSerializer(many=True, read_only=True)

    class Meta:
        model = TechnicianCard
        fields = ['id', 'date', 'tasks']
        
        