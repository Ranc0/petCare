from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Store, Product
from django.contrib.auth import get_user_model

User = get_user_model()
from ..serializers import StoreSerializer, ProductSerializer
from rest_framework import status
from PIL import Image
import os

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
        logo = store.logo.url if store.logo else None
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
    if user != store.user:
        return Response({"message":"user does not have this store"}, status= status.HTTP_401_UNAUTHORIZED)
    products = Product.objects.filter(user = user)
    for product in products:
        product.delete()
    store.delete()
    return Response({"message":"store deleted successfully"}, status= status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_store(request, id):
    store = get_object_or_404(Store, id = id)
    logo = store.logo.url if store.logo else None
    user = store.user
    products = Product.objects.filter(user = user)

    holder = []
    for product in products:
        photo = product.photo.url if product.photo else None
        product = ProductSerializer(product).data
        product.update({"photo":photo})
        holder.append(product)
    response = StoreSerializer(store).data
    response.update({'logo':logo})
    response.update({'products':holder})
    return Response(response, status= status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_store_photo(request, id):
    store = get_object_or_404(Store, id = id)
    photo = request.FILES.get('logo')
    if not photo:
        return Response({"message": "photo is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate the uploaded file as an image
        image = Image.open(photo)
        image.verify()  # Verify the image integrity

        # Delete the old photo if it exists
        if store.logo and os.path.isfile(store.logo.path):
            os.remove(store.logo.path)

        # Update the photo field
        store.logo = photo
        store.save()

        # Serialize the updated pet object
        response = StoreSerializer(store).data
        response.update({"logo": store.logo.url if store.logo else None})
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)