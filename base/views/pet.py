from django.forms import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import PetSerializer
from ..models import Pet , CatVaccination , DogVaccination
from rest_framework import status
from PIL import Image

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_pet (request):
    user = request.user
    obj = PetSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        obj.update({ "user" : user }) 
        photo = request.FILES.get('photo')
        obj.pop('photo')
        pet = Pet.objects.create(**obj , photo = photo)
        if pet.type == 'cat':
            vaccination = CatVaccination.objects.create(pet = pet)
        else :
            vaccination = DogVaccination.objects.create(pet = pet)

        return Response(PetSerializer(pet).data , status=status.HTTP_201_CREATED )
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_pet (request , id ):
    #you do it , make sure the pet the user owns the pet he's updating 
    try:
        pet = Pet.objects.get(id = id)
        if pet.user != request.user:
            return Response({"message":"user does not have this pet"}, status= status.HTTP_404_NOT_FOUND)
    
        obj = PetSerializer(data=request.data, many=False)
        if obj.is_valid():
            for attr, value in obj.data.items():
                setattr(pet, attr, value)
            pet.save()
            return Response(PetSerializer(pet).data, status=200) 
        else:
            return Response(obj.errors, status=400)

    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status=status.HTTP_404_NOT_FOUND)
    

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_pet (request , id ):
    #you do it , make sure the pet the user owns the pet he's deleting
    try:
        pet = Pet.objects.get(id=id)
    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status= status.HTTP_404_NOT_FOUND)
    if pet.user != request.user:
        return Response({"message": "user does not have the pet"}, status= status.HTTP_409_CONFLICT)
    
    pet.delete()
    return Response({"message":"pet deleted suceessfully"}, status= status.HTTP_200_OK)
    pass

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_pet (request , id ):
    #you do it 
    try:
        pet = Pet.objects.get(id=id)
    except Pet.DoesNotExist:
        return Response({"message": "pet not found"}, status= status.HTTP_404_NOT_FOUND)
    return Response(PetSerializer(pet).data , status=status.HTTP_200_OK )
    
    
