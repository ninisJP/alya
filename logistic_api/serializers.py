# serializers.py
from rest_framework import serializers
from accounting_order_sales.models import SalesOrderItem
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from logistic_suppliers.models import Suppliers

class RequirementOrderSimpleSerializer(serializers.ModelSerializer):
    codigo_sap = serializers.SerializerMethodField(source='sapcode')
    detalles = serializers.SerializerMethodField(source='detail')
    cliente = serializers.SerializerMethodField(source='name')
    orden_venta = serializers.SerializerMethodField(source='client')
    numero_orden = serializers.CharField(source='order_number')
    fecha_solicitud = serializers.DateField(source='requested_date')
    
    class Meta:
        model = RequirementOrder
        fields = ['numero_orden', 'estado', 'fecha_solicitud', 'notes', 'codigo_sap', 'detalles', 'cliente', 'orden_venta']

    def get_codigo_sap(self, obj):
        return obj.sales_order.sapcode if obj.sales_order else None

    def get_detalles(self, obj):
        return obj.sales_order.detail if obj.sales_order else None

    def get_proyecto_id(self, obj):
        return obj.sales_order.project.id if obj.sales_order and obj.sales_order.project else None
    
    def get_cliente(self, obj):
        return obj.sales_order.project.name if obj.sales_order and obj.sales_order.project else None
    
    def get_orden_venta(self, obj):
        return obj.sales_order.project.client.legal_name if obj.sales_order and obj.sales_order.project else None


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suppliers
        fields = ['id','name', 'document']  # Solo traemos el nombre y el RUC

class SalesOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = ['id', 'description', 'sap_code', 'amount', 'price', 'price_total', 'unit_of_measurement']

class RequirementOrderItemSerializer(serializers.ModelSerializer):
    sales_order_item = SalesOrderItemSerializer(read_only=True)  # No editable
    supplier = SupplierSerializer(read_only=True)  # Solo lectura
    estado = serializers.CharField()  # Permitimos modificar el estado

    class Meta:
        model = RequirementOrderItem
        fields = ['id', 'sales_order_item', 'sap_code', 'quantity_requested', 'notes', 'supplier', 'estado', 'price']

