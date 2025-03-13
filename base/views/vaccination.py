from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import CatVaccinationSerializer , DogVaccinationSerializer
from ..models import Pet , CatVaccination , DogVaccination
from rest_framework import status


#getters should be made as well (use the serializer - so easy)

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_cat_vaccination (request , id):
    user = request.user
    pet = Pet.objects.filter(id=id)
    pet = pet[0]
    if not pet :
        return Response({"message":"no such id"}, status=status.HTTP_404_NOT_FOUND)
    if pet.user != user :
            return Response({"message":"you don't have access to update this pet"}, status = status.HTTP_401_UNAUTHORIZED)
    if pet.type !='cat':
         return Response({"message":"this pet is a dog not a cat !"}, status = status.HTTP_400_BAD_REQUEST)

    obj = CatVaccinationSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        CatVaccination.objects.update_or_create(id=id,pet = pet ,defaults=obj)
        vac = CatVaccination.objects.get(id = id)

        return Response(CatVaccinationSerializer(vac).data , status=status.HTTP_202_ACCEPTED)
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_dog_vaccination (request , id):
    user = request.user
    pet = Pet.objects.filter(id=id)
    pet=pet[0]
    if not pet :
        return Response({"message":"no such id"}, status=status.HTTP_404_NOT_FOUND)
    if pet.user != user :
            return Response({"message":"you don't have access to update this pet"}, status = status.HTTP_401_UNAUTHORIZED)
    if pet.type !='dog':
         return Response({"message":"this pet is a cat not a dog !"}, status = status.HTTP_400_BAD_REQUEST)
    obj = DogVaccinationSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        DogVaccination.objects.update_or_create(id=id , pet = pet , defaults=obj)
        vac = DogVaccination.objects.get(id = id)
        return Response(DogVaccinationSerializer(vac).data , status=status.HTTP_202_ACCEPTED)
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)


