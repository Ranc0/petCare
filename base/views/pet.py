from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import PetSerializer, CatVaccinationSerializer, DogVaccinationSerializer
from ..models import Pet , CatVaccination , DogVaccination
from rest_framework import status
from PIL import Image
import os
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_pet(request):
    user = request.user
    serializer = PetSerializer(data=request.data)

    if serializer.is_valid():
        pet = serializer.save(user=user, photo=None)  # Let DRF handle creation

        if pet.type == 'cat':
            CatVaccination.objects.create(pet=pet)
        else:
            DogVaccination.objects.create(pet=pet)

        return Response(PetSerializer(pet).data, status=status.HTTP_201_CREATED)

    return Response({"message": "form is not valid"}, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_pet (request , id ):
    pet = get_object_or_404(Pet, id = id)
    if request.user != pet.user:
        return Response({"message":"user does not have this pet"}, status= status.HTTP_401_UNAUTHORIZED)
    obj = PetSerializer(data=request.data, many = False)
    if obj.is_valid():
        for attr, value in obj.data.items():
            setattr(pet, attr, value)
        pet.save()
        response = PetSerializer(pet).data

        photo = None

        if pet.photo:
            photo = f"{settings.DOMAIN}{pet.photo.url}"
        response.update({'photo':photo})
        return Response(response, status= status.HTTP_200_OK)
    else:
        return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_pet (request , id ):
    pet = get_object_or_404(Pet, id = id)
    if request.user != pet.user:
        return Response({"message":"user does not have this pet"}, status= status.HTTP_401_UNAUTHORIZED)
    pet.delete()
    return Response({"message":"pet deleted successfully"}, status= status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_pet (request , id ):
    pet = get_object_or_404(Pet, id = id)
    response = PetSerializer(pet).data

    photo = None

    if pet.photo:
        photo = f"{settings.DOMAIN}{pet.photo.url}"
    response.update({'photo':photo})
    return Response(response, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_user_pets (request):
    user = request.user
    response =[]
    pets = Pet.objects.filter(user = user)
    for pet in pets:
        pet1 = PetSerializer(pet).data
        photo = None

        if pet.photo:
            photo = f"{settings.DOMAIN}{pet.photo.url}"
        pet1.update({'photo':photo})

        response.append(pet1)
    return Response( response, status= status.HTTP_200_OK )

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_pet_photo(request, id):
    pet = Pet.objects.filter(id = id)
    if pet:
        pet = pet[0]
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
        if pet.photo and os.path.isfile(pet.photo.path):
            os.remove(pet.photo.path)

        # Update the photo field
        pet.photo = photo
        pet.save()

        # Serialize the updated pet object
        response = PetSerializer(pet).data
        ph = None
        if pet.photo:
            ph = f"{settings.DOMAIN}{pet.photo.url}"
        response.update({"photo": ph})
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_vaccinations (request , id):
    try:
        pet = Pet.objects.get(id = id)
    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status= status.HTTP_404_NOT_FOUND)
    if request.user != pet.user:
        return Response({"message": "user does not have the pet"}, status= status.HTTP_401_UNAUTHORIZED)
    if pet.type == 'cat':
        vaccination1 = CatVaccination.objects.get(pet = pet)
        response = CatVaccinationSerializer(vaccination1).data
    elif pet.type == 'dog':
        vaccination2 = DogVaccination.objects.get(pet = pet)
        response = DogVaccinationSerializer(vaccination2).data
    return Response(response, status= 200)

@permission_classes ([IsAuthenticated])
@api_view(['PUT'])
def update_vaccinations(request, id):
    try:
        pet = Pet.objects.get(id = id)
    except Pet.DoesNotExist:
        return Response({'message':'pet not found'}, status= 404)

    if request.user != pet.user:
        return Response({'message':'user does not have the pet'}, status = 401)
    if pet.type == 'cat':
        vaccination = CatVaccination.objects.get(pet = pet)
        obj = CatVaccinationSerializer(data=request.data, many = False)
    elif pet.type == 'dog':
        vaccination = DogVaccination.objects.get(pet = pet)
        obj = DogVaccinationSerializer(data=request.data, many = False)

    if obj.is_valid():
        for attr, value in obj.data.items():
            setattr(vaccination, attr, value)
        vaccination.save()
        if pet.type == 'cat':
            response = CatVaccinationSerializer(vaccination).data
        else:
            response = DogVaccinationSerializer(vaccination).data
        return Response(response , status = 200)
    else:
        return Response(obj.errors, status=status.HTTP_400_BAD_REQUEST)

