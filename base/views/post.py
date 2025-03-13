from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , AdoptionPost , BreedingPost
from django.contrib.auth.models import User
from ..serializers import PetSerializer
from rest_framework import status



@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_adoption_post (request , id):
    user = request.user
    pet = Pet.objects.filter(id=id)
    if not pet :
        return Response({"message":"no such id"}, status=status.HTTP_404_NOT_FOUND)
    pet = pet[0]
    details = request.data["details"]
    AdoptionPost.objects.create(pet = pet , user = user , details = details)
    serialized_pet = PetSerializer( pet, many=False).data
    serialized_pet.update({"details":details})
    return Response(serialized_pet , status=status.HTTP_201_CREATED)

#delete post should be made 
#no need to make a view for updating 
#a getter should be made to list all the posts available
#getters can be separated for dogs and cats ( filters ) 
# same process for breeding posts (I made the model for you)
