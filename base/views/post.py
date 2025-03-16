from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , AdoptionPost , BreedingPost
from django.contrib.auth.models import User
from ..serializers import PetSerializer, AdoptionPostSerializer
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

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_adoption_post (request , id):
    adoption_post = AdoptionPost.objects.filter(id = id)
    if not adoption_post:
        return Response({"message" : "no such id"} , status = status.HTTP_404_NOT_FOUND)
    if adoption_post.user != request.user:
        return Response({"message":"user does not have this post"}, status = status.HTTP_401_UNAUTHORIZED)
    adoption_post.delete()
    return Response({"message" : "post deleted successfully"})

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_adoption_posts (request):
    posts = AdoptionPost.objects.all()
    response = {}
    for post in posts:
        pet = PetSerializer(Pet.objects.get(id = post.pet_id)).data
        username = post.user.username
        holder = pet
        holder.update({"username":username})
        holder.update({"details":post.details})
        response.update(holder)
    return Response(response, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_adoption_post (request, id):
    post = AdoptionPost.objects.filter(id = id)
    if not post:
        return Response({"message":"no such id"}, status= status.HTTP_404_NOT_FOUND)
    post = post[0]
    username = post.user.username
    pet = PetSerializer(Pet.objects.get(id = post.pet.id)).data
    response = pet
    response.update({"username":username})
    response.update({"datails":post.details})
    return Response(response, status= status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def adoption_filter (request):
    filter_params = {
        'type': request.data.get('type',None),
        'breed': request.data.get('breed',None),
        'gender': request.data.get('gender',None),
    }
    birth_date = request.data.get('birth_date',None)
    if birth_date:
        filter_params['birth_date__lte'] = birth_date

    filter_params = {key: value for key, value in filter_params.items() if value is not None}
    pets = Pet.objects.filter(**filter_params)
    response = {}
    for pet in pets:
        post = AdoptionPost.objects.filter(pet_id = pet.id)
        if post:
            post = post[0]
            username = pet.user.username
            pet = PetSerializer(pet).data
            holder = pet
            holder.update({"username":username})
            holder.update({"details":post.details})
            response.update(holder)
    return Response(response, status= 200)