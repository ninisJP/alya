# serializers.py
from rest_framework import serializers
from accounting_order_sales.models import SalesOrderItem
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from logistic_suppliers.models import Suppliers

class RequirementOrderSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequirementOrder
        fields = ['order_number', 'estado', 'requested_date', 'notes']

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

