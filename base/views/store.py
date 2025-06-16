from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Store, Product
from django.contrib.auth.models import User
from ..serializers import StoreSerializer, ProductSerializer
from rest_framework import status

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def create_store (request):
    user = request.user
    if Store.objects.filter(user = user).exists():
        return Response({"message": "A store already exists for this user."}, status=status.HTTP_400_BAD_REQUEST)
    obj = StoreSerializer(data = request.data, many = False)
    if obj.is_valid():
        obj = obj.data
        obj.update({ "user" : user })
        Store.objects.create(**obj)
        store = Store.objects.last()
        response = StoreSerializer(store).data
        logo = store.logo if store.logo else None
        response.update({'logo':logo})
        response.update({'products':[]})
        return Response(response , status=status.HTTP_201_CREATED)
    else:
        return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_store(request,id):
    user = request.user
    store = get_object_or_404(Store, id = id)
    if request.user != store.user:
        return Response({"message":"user does not have this store"}, status= status.HTTP_401_UNAUTHORIZED)
    products = Product.objects.filter(user = user)
    for product in products:
        product.delete()
    store.delete()
    return Response({"message":"store deleted successfully"}, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_store(request, id):
    user = request.user
    store = get_object_or_404(Store, id = id)
    logo = store.logo if store.logo else None
    products = Product.objects.filter(user = user)

    holder = []
    for product in products:
        photo = product.photo if product.photo else None
        product = ProductSerializer(product).data
        product.update({"photo":photo})
        holder.append(product)
    response = StoreSerializer(store).data
    response.update({'logo':logo})
    response.update({'products':holder})
    return Response(response, status= status.HTTP_200_OK)
