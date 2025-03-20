from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , Product
from django.contrib.auth.models import User
from ..serializers import ProductSerializer
from rest_framework import status

#views to add :
#add product
#update product
#delete product
#getters (filters must be applied)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_product (request):
    user = request.user
    obj = ProductSerializer(data = request.data, many = False)
    if obj.is_valid():
        obj = obj.data
        obj.update({ "user" : user })
        Product.objects.create(**obj)
        return Response({"message":"product added successfully"} , status=status.HTTP_201_CREATED)
    else:
        return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_product (request, id):
    product = get_object_or_404(Product, id=id)
    if request.user != product.user:
        return Response({"message":"user does not have this product"}, status= status.HTTP_401_UNAUTHORIZED)
    product.delete()
    return Response({"message":"product deleted successfully"}, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_products (request):
    products = Product.objects.all()
    response = []
    for product in products:
        photo = product.photo if product.photo else None
        username = product.user.username
        product = ProductSerializer(product).data
        product.update({"photo":photo})
        product.update({"username":username})
        response.append(product)
    return Response(response, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_product (request, id):
    product = get_object_or_404(Product, id=id)
    photo = product.photo if product.photo else None
    username = product.user.username
    product = ProductSerializer(product).data
    product.update({"photo":photo})
    product.update({"username":username})
    return Response(product, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def product_filter (request):
    filter_params = {
        'category': request.data.get('category',None),
    }
    price = request.data.get('price',None)
    if price:
        filter_params['price__lte'] = price
    filter_params = {key: value for key, value in filter_params.items() if value is not None}
    products = Product.objects.filter(**filter_params).order_by('price')
    response = []
    for product in products:
        photo = product.photo if product.photo else None
        username = product.user.username
        product = ProductSerializer(product).data
        product.update({"photo":photo})
        product.update({"username":username})
        response.append(product)
    return Response(response, status= status.HTTP_200_OK)
