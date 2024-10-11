from django.contrib.auth.decorators import login_not_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from logistic_inventory.models import Subtype, Type, Brand, Item
from logistic_inventory.models import Subtype, Type, Brand
from .serializers import SubtypeSerializer, TypeSerializer, ItemSerializer, BrandSerializer


@login_not_required
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_list(request):
	list_subtype = Subtype.objects.all()
	list_type = Type.objects.all()
	list_brand = Brand.objects.all()

	serializer_subtype = SubtypeSerializer(list_subtype, many=True)
	serializer_type = TypeSerializer(list_type, many=True)
	serializer_brand = BrandSerializer(list_brand, many=True)

	context = {
			"subtype": serializer_subtype.data,
			"type": serializer_type.data,
			"brand": serializer_brand.data,
		}
	return Response(context, status=status.HTTP_200_OK)

@login_not_required
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def item_get(request):
	item = get_object_or_404(Item, id=request.data["id"])
	serializer = ItemSerializer(item)
	context = serializer.data
	return Response(context, status=status.HTTP_200_OK)

@login_not_required
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def item_new(request):
	serializer = ItemSerializer(data=request.data)

	if not serializer.is_valid():
		return Response({}, status=status.HTTP_400_BAD_REQUEST)

	#serializer.save()
	return Response({}, status=status.HTTP_200_OK)
