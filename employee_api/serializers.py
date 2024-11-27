from rest_framework import serializers
from django.contrib.auth.models import User
from follow_control_technician.models import TechnicianCard, TechnicianCardTask, TechnicianTask
from follow_control_card.models import Task, CardTaskOrder, Card
from accounting_order_sales.models import SalesOrder

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
        
                
# Cards
class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'name', 'description']

class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = [
            'id', 'sapcode', 'project', 'detail', 'date', 
            'total_sales_order', 'days', 'created_at', 'is_active'
        ]
        
class TaskSerializer(serializers.ModelSerializer):
    cards = CardSerializer(many=True, read_only=True)  
    sale_order = SalesOrderSerializer(read_only=True)  
    user = UserSerializer(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'verb', 'object', 'sale_order', 'measurement', 
            'task_time', 'user', 'cards'
        ]

    def validate_task_time(self, value):
        if value and value < 0:
            raise serializers.ValidationError("El tiempo de tarea debe ser positivo.")
        return value
    
# Card Task Order
class CardTaskOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardTaskOrder
        fields = ['card','task','order','state']
        