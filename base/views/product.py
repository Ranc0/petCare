from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , Product, Store
from django.contrib.auth.models import User
from ..serializers import ProductSerializer, StoreSerializer
from rest_framework import status
from django.db.models import Q
from django.shortcuts import get_object_or_404

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
        product = Product.objects.last()
        photo = product.photo if product.photo else None
        response = ProductSerializer(product).data
        response.update({'photo':photo})
        store = Store.objects.get(user=product.user)
        logo = store.logo if store.logo else None
        response.update({"store_name":store.store_name})
        response.update({"location":store.location})
        response.update({"logo":logo})
        return Response(response , status=status.HTTP_201_CREATED)
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
def get_products(request):
    products = Product.objects.all()
    response = []

    for product in products:
        serialized = ProductSerializer(product).data
        serialized["photo"] = product.photo.url if product.photo else None
        response.append(serialized)

    return Response(response, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_product (request, id):
    product = get_object_or_404(Product, id=id)
    photo = product.photo if product.photo else None
    store = Store.objects.get(user=product.user)
    logo = store.logo if store.logo else None
    response = ProductSerializer(product).data
    response.update({"photo":photo})
    response.update({"store_name":store.store_name})
    response.update({"location":store.location})
    response.update({"logo":logo})
    return Response(response, status= status.HTTP_200_OK)

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
        response.append(product)
    return Response(response, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def product_search(request):
    text = request.data.get('text',None)
    if text is not None:
        products = Product.objects.filter(Q(name__icontains= text)|Q(details__icontains= text)|Q(category__icontains = text))
    else:
        products = Product.objects.all()
    response = []
    for product in products:
        photo = product.photo if product.photo else None
        product = ProductSerializer(product).data
        product.update({"photo":photo})
        response.append(product)
    return Response(response, status= status.HTTP_200_OK)
