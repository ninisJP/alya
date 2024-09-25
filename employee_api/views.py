from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_not_required
from .serializers import UserSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .serializers import TechnicianCardSerializer
from employee.models import Technician
from follow_control_technician.models import TechnicianCard


@login_not_required
@api_view(['POST'])
def login_employee(request):
    
    user = get_object_or_404(User, username=request.data['username'])
    
    if not user.check_password(request.data['password']):
        return Response({"message": "Contraseña incorrecta"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    
    return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)

@login_not_required
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def technician_card(request):
    # Obtener el perfil del técnico autenticado
    technician = get_object_or_404(Technician, user=request.user)

    # Filtrar las TechnicianCard asociadas al técnico
    technician_cards = TechnicianCard.objects.filter(technician=technician)

    # Serializar las tarjetas con sus tareas
    serializer = TechnicianCardSerializer(technician_cards, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


 # Consumir api
@login_not_required
@csrf_exempt
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_technician_card(request):
    # Obtener el técnico asociado al usuario autenticado
    technician = get_object_or_404(Technician, user=request.user)

    # Filtrar las tarjetas del técnico
    technician_cards = TechnicianCard.objects.filter(technician=technician)

    # Serializar los datos
    serializer = TechnicianCardSerializer(technician_cards, many=True, context={'request': request})

    # Retornar la respuesta con los datos serializados
    return Response(serializer.data, status=200)