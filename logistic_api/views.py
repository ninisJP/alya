# views.py
from rest_framework import generics
from logistic_requirements.models import RequirementOrder, RequirementOrderItem
from .serializers import RequirementOrderSimpleSerializer, RequirementOrderItemSerializer
from django.contrib.auth.decorators import login_not_required
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status

@login_not_required
@api_view(['GET'])
@permission_classes([AllowAny]) 
def requirement_order_list_view(request):
    requirement_orders = RequirementOrder.objects.filter(estado=False)
    serializer = RequirementOrderSimpleSerializer(requirement_orders, many=True)
    return Response(serializer.data)

@login_not_required
@api_view(['GET'])
@permission_classes([AllowAny])
def get_requirement_order_items_view(request, order_number):
    try:
        requirement_order = RequirementOrder.objects.get(order_number=order_number)
        items = requirement_order.items.all()
        serializer = RequirementOrderItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except RequirementOrder.DoesNotExist:
        return Response({'error': 'Orden no encontrada'}, status=status.HTTP_404_NOT_FOUND)

@login_not_required
@api_view(['PUT'])
@permission_classes([AllowAny])
def edit_requirement_order_item_view(request, item_id):
    try:
        item = RequirementOrderItem.objects.get(id=item_id)
    except RequirementOrderItem.DoesNotExist:
        return Response({'error': 'Item no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    # Utilizamos el serializador con partial=True para actualizar solo los campos permitidos
    serializer = RequirementOrderItemSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        print(serializer.errors)  # Depuración de errores
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

