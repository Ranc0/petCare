from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , Product, Store
from django.contrib.auth import get_user_model

User = get_user_model()
from ..serializers import ProductSerializer, StoreSerializer
from rest_framework import status
from django.db.models import Q
from PIL import Image
import os
from django.shortcuts import get_object_or_404
from django.conf import settings


#views to add :
#add product
#update product
#delete product
#getters (filters must be applied)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_product (request):
    user = request.user
    store = get_object_or_404(Store, user = user)
    obj = ProductSerializer(data = request.data, many = False)
    if obj.is_valid():
        obj = obj.data
        obj.update({ "user" : user })
        Product.objects.create(**obj)
        product = Product.objects.last()
        photo = None
        if product.photo :
            photo = f"{settings.DOMAIN}{product.photo.url}"

        response = ProductSerializer(product).data
        #store = Store.objects.get(user=product.user)
        logo = None
        if store.logo:
           logo = f"{settings.DOMAIN}{store.logo.url}"
        response.update({"photo":photo})
        response.update({"store_name":store.store_name})
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

#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_products(request):
    products = Product.objects.all()
    response = []


    for product in products:
        holder = {}
        photo = None
        if product.photo :
            photo = f"{settings.DOMAIN}{product.photo.url}"
        holder.update({"id":product.id})
        holder.update({"photo":photo})
        holder.update({"name":product.name})
        holder.update({"price":product.price})
        response.append(holder)

    return Response(response, status=status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_product (request, id):
    product = get_object_or_404(Product, id=id)
    photo = None
    if product.photo:
        photo = f"{settings.DOMAIN}{product.photo.url}"
    store = Store.objects.get(user=product.user)
    logo = None
    if store.logo:
        logo = f"{settings.DOMAIN}{store.logo.url}"
    response = ProductSerializer(product).data
    response.update({"photo":photo})
    response.update({"store_name":store.store_name})
    response.update({"logo":logo})
    response.update({"country":product.user.country})
    return Response(response, status= status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def product_filter (request):
    filter_params = {
        'category': request.data.get('category',None),
    }
    price = request.data.get('price',None)
    country = request.data.get('country',None)
    if price:
        filter_params['price__lte'] = price
    if country:
        filter_params['user__country'] = country

    filter_params = {key: value for key, value in filter_params.items() if value is not None}
    products = Product.objects.filter(**filter_params)

    response = []
    for product in products:
        photo = None
        if product.photo:
            photo = f"{settings.DOMAIN}{product.photo.url}"

        product = ProductSerializer(product).data
        product.update({"photo":photo})
        response.append(product)
    return Response(response, status= status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def product_search(request):
    text = request.data.get('text',None)
    if text is not None:
        products = Product.objects.filter(Q(name__icontains= text)|Q(details__icontains= text)|Q(category__icontains = text))
    else:
        products = Product.objects.all()
    response = []
    for product in products:
        photo = None
        if product.photo:
            photo = f"{settings.DOMAIN}{product.photo.url}"
        product = ProductSerializer(product).data
        product.update({"photo":photo})
        response.append(product)
    return Response(response, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_product_photo(request, id):
    product = Product.objects.filter(id = id)
    if product:
        product = product[0]
    else:
        return Response({"message":"pet not found"}, status= status.HTTP_404_NOT_FOUND)
    photo = request.FILES.get('photo')
    if not photo:
        return Response({"message": "photo is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate the uploaded file as an image
        image = Image.open(photo)
        image.verify()  # Verify the image integrity

        # Delete the old photo if it exists
        if product.photo and os.path.isfile(product.photo.path):
            os.remove(product.photo.path)

        # Update the photo field
        product.photo = photo
        product.save()

        # Serialize the updated pet object
        response = ProductSerializer(product).data
        ph = None
        if product.photo:
             ph= f"{settings.DOMAIN}{product.photo.url}"
        response.update({"photo": ph})
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)