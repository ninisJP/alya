from rest_framework import serializers

from logistic_inventory.models import Subtype, Type, Item, Brand

class SubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtype
        fields = ['id', 'name', 'type']

class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name', 'category']

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = ['id', 'name']

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['brand', 'description', 'item_id', 'quantity', 'subtype', 'unit', 'price_per_day', 'price', 'life_time']
