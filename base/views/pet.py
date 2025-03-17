from django.forms import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import PetSerializer
from ..models import Pet , CatVaccination , DogVaccination
from rest_framework import status
from PIL import Image
import os

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_pet (request):
    user = request.user
    obj = PetSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        obj.update({ "user" : user }) 
        #photo = request.FILES.get('photo')
        #obj.pop('photo')
        pet = Pet.objects.create(**obj)# , photo = photo)
        if pet.type == 'cat':
            vaccination = CatVaccination.objects.create(pet = pet)
        else :
            vaccination = DogVaccination.objects.create(pet = pet)

        return Response({"message":"pet added successfully"} , status=status.HTTP_201_CREATED )
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_pet (request , id ):
    try:
        pet = Pet.objects.get(id = id)
        if pet.user != request.user:
            return Response({"message":"user does not have this pet"}, status= status.HTTP_401_UNAUTHORIZED)
    
        obj = PetSerializer(data=request.data, many=False)
        if obj.is_valid():
            for attr, value in obj.data.items():
                setattr(pet, attr, value)
            pet.save()
            response = PetSerializer(pet).data
            response.update({"photo":pet.photo.url if pet.photo else None})
            return Response(response, status=200) 
        else:
            return Response(obj.errors, status=status.HTTP_400_BAD_REQUEST)

    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status=status.HTTP_404_NOT_FOUND)
    

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_pet (request , id ):
    try:
        pet = Pet.objects.get(id=id)
    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status= status.HTTP_404_NOT_FOUND)
    if pet.user != request.user:
        return Response({"message": "user does not have the pet"},status= status.HTTP_401_UNAUTHORIZED)
    
    pet.delete()
    return Response({"message":"pet deleted suceessfully"}, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_pet (request , id ):
    try:
        pet = Pet.objects.get(id=id)
    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status= status.HTTP_404_NOT_FOUND)
    if request.user != pet.user:
        return Response({"message": "user does not have the pet"}, status= status.HTTP_401_UNAUTHORIZED)
    response = PetSerializer(pet).data
    response.update({"photo":pet.photo.url if pet.photo else None})
    return Response( response , status=status.HTTP_200_OK )
    
    
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
        response.update({"photo": pet.photo.url if pet.photo else None})
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)