import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , AdoptionPost , BreedingPost
from django.contrib.auth import get_user_model

User = get_user_model()
from ..serializers import PetSerializer, AdoptionPostSerializer
from rest_framework import status
from django.db.models import Q
from django.conf import settings



@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_adoption_post (request , id):
    user = request.user
    pet = Pet.objects.filter(id=id)
    if not pet :
        return Response({"message":"no such id"}, status=status.HTTP_404_NOT_FOUND)
    pet = pet[0]
    details = request.data["details"]
    post = AdoptionPost.objects.create(pet = pet , user = user , details = details)
    serialized_pet = PetSerializer( pet, many=False).data
    response = serialized_pet
    photo = None
    if pet.photo :
        photo = f"{settings.DOMAIN}{pet.photo.url}"

    response.update({"photo":photo})
    response.update({"details":details})
    response.update({"id":post.id})
    return Response(response , status=status.HTTP_201_CREATED)

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
    adoption_post = adoption_post[0]
    if adoption_post.user != request.user:
        return Response({"message":"user does not have this post"}, status = status.HTTP_401_UNAUTHORIZED)
    adoption_post.delete()
    return Response({"message" : "post deleted successfully"})

#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_adoption_posts (request):
    posts = AdoptionPost.objects.all()
    response = []
    for post in posts:
        pet = Pet.objects.get(id = post.pet_id)
        serialized_pet = PetSerializer(pet).data
        username = post.user.username
        holder = serialized_pet
        photo = None
        if pet.photo :
            photo = f"{settings.DOMAIN}{pet.photo.url}"
        
        holder.update({"photo":photo})
        holder.update({"username":username})
        holder.update({"details":post.details})
        holder.update({"id":post.id})
        holder.update({"logo":post.user.user_photo})
        response.append(holder)
    return Response(response, status= status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_adoption_post (request, id):
    post = AdoptionPost.objects.filter(id = id)
    if not post:
        return Response({"message":"no such id"}, status= status.HTTP_404_NOT_FOUND)
    post = post[0]
    username = post.user.username
    pet = Pet.objects.get(id = post.pet_id)
    serialized_pet = PetSerializer(pet).data
    response = serialized_pet
    photo = None
    if pet.photo :
        photo = f"{settings.DOMAIN}{pet.photo.url}"


    response.update({"photo":photo})
    response.update({"username":username})
    response.update({"datails":post.details})
    response.update({"id":post.id})
    response.update({"logo":post.user.user_photo})

    return Response(response, status= status.HTTP_200_OK)

#@permission_classes([IsAuthenticated])
@api_view(['POST'])
def adoption_filter (request):
    filter_params = {
        'type': request.data.get('type',None),
        'breed': request.data.get('breed',None),
        'gender': request.data.get('gender',None),
    }
    birth_date = request.data.get('birth_date',None)
    country = request.data.get('country',None)
    if country:
        filter_params['user__country'] = country
    if birth_date:
        try:
            birth_date_obj = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
            #print(birth_date_obj)
            #print( Pet.objects.get(id=9).birth_date)
            filter_params['birth_date__lte'] = birth_date_obj
        except ValueError:
            return Response({"message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    filter_params = {key: value for key, value in filter_params.items() if value is not None}
    pets = Pet.objects.filter(**filter_params)
    response = []
    for pet in pets:
        post = AdoptionPost.objects.filter(pet_id = pet.id)
        if post:
            post = post[0]
            username = pet.user.username
            serialized_pet = PetSerializer(pet).data
            holder = serialized_pet
            photo = None
            if pet.photo :
                photo = f"{settings.DOMAIN}{pet.photo.url}"

            holder.update({"photo":photo})
            holder.update({"username":username})
            holder.update({"details":post.details})
            holder.update({"logo":post.user.user_photo})

            response.append(holder)
    return Response(response, status= 200)

@api_view(['POST'])
def adoption_post_search(request):
    text = request.data.get('text',None)
    if text is not None:
        pets = Pet.objects.filter(Q(type__icontains= text)|Q(breed__icontains= text)|Q(gender__icontains= text)|Q(name__icontains= text))
    else:
        pets= Pet.objects.all()
    response = []
    for pet in pets:
        username = pet.user.username
        post = AdoptionPost.objects.filter(pet = pet)
        if not post:
            continue
        post = post[0]
        serialized_pet = PetSerializer(pet).data
        holder = serialized_pet
        photo = None
        if pet.photo :
            photo = f"{settings.DOMAIN}{pet.photo.url}"

        holder.update({"photo":photo})
        holder.update({"username":username})
        holder.update({"details":post.details})
        holder.update({"id":post.id})
        holder.update({"logo":post.user.user_photo})

        response.append(holder)
    return Response(response, status= status.HTTP_200_OK)

#############################################################################################

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def add_breeding_post (request , id):
    user = request.user
    pet = Pet.objects.filter(id=id)
    if not pet :
        return Response({"message":"no such id"}, status=status.HTTP_404_NOT_FOUND)
    pet = pet[0]
    details = request.data["details"]
    post = BreedingPost.objects.create(pet = pet , user = user , details = details)
    serialized_pet = PetSerializer( pet, many=False).data
    response = serialized_pet
    photo = None
    if pet.photo :
        photo = f"{settings.DOMAIN}{pet.photo.url}"

    response.update({"photo":photo})
    response.update({"details":details})
    response.update({"id":post.id})
    return Response(response , status=status.HTTP_201_CREATED)

@permission_classes([IsAuthenticated])
@api_view(['DELETE'])
def delete_breeding_post (request , id):
    breeding_post = BreedingPost.objects.filter(id = id)
    if not breeding_post:
        return Response({"message" : "no such id"} , status = status.HTTP_404_NOT_FOUND)
    breeding_post = breeding_post[0]
    if breeding_post.user != request.user:
        return Response({"message":"user does not have this post"}, status = status.HTTP_401_UNAUTHORIZED)
    breeding_post.delete()
    return Response({"message" : "post deleted successfully"})

@api_view(['GET'])
def get_breeding_posts (request):
    posts = BreedingPost.objects.all()
    response = []
    for post in posts:
        pet = Pet.objects.get(id = post.pet_id)
        serialized_pet = PetSerializer(pet).data
        username = post.user.username
        holder = serialized_pet
        photo = None
        if pet.photo :
            photo = f"{settings.DOMAIN}{pet.photo.url}"

        holder.update({"photo":photo})
        holder.update({"username":username})
        holder.update({"details":post.details})
        holder.update({"id":post.id})
        holder.update({"logo":post.user.user_photo})

        response.append(holder)
    return Response(response, status= status.HTTP_200_OK)

@api_view(['GET'])
def get_breeding_post (request, id):
    post = BreedingPost.objects.filter(id = id)
    if not post:
        return Response({"message":"no such id"}, status= status.HTTP_404_NOT_FOUND)
    post = post[0]
    username = post.user.username
    pet = Pet.objects.get(id = post.pet_id)
    serialized_pet = PetSerializer(pet).data
    response = serialized_pet
    photo = None
    if pet.photo :
        photo = f"{settings.DOMAIN}{pet.photo.url}"

    response.update({"photo":photo})
    response.update({"username":username})
    response.update({"datails":post.details})
    response.update({"id":post.id})
    response.update({"logo":post.user.user_photo})

    return Response(response, status= status.HTTP_200_OK)


@api_view(['POST'])
def breeding_filter (request):
    filter_params = {
        'type': request.data.get('type',None),
        'breed': request.data.get('breed',None),
        'gender': request.data.get('gender',None),
    }
    birth_date = request.data.get('birth_date',None)
    country = request.data.get('country',None)
    if country:
        filter_params['user__country'] = country
    if birth_date:
        try:
            birth_date_obj = datetime.datetime.strptime(birth_date, '%Y-%m-%d').date()
            filter_params['birth_date__lte'] = birth_date_obj
        except ValueError:
            return Response({"message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

    filter_params = {key: value for key, value in filter_params.items() if value is not None}
    pets = Pet.objects.filter(**filter_params)
    response = []
    for pet in pets:
        post = BreedingPost.objects.filter(pet_id = pet.id)
        if post:
            post = post[0]
            username = pet.user.username
            serialized_pet = PetSerializer(pet).data
            holder = serialized_pet
            photo = None
            if pet.photo :
                photo = f"{settings.DOMAIN}{pet.photo.url}"

            holder.update({"photo":photo})
            holder.update({"username":username})
            holder.update({"details":post.details})
            holder.update({"logo":post.user.user_photo})

            response.append(holder)
    return Response(response, status= 200)

@api_view(['POST'])
def breeding_post_search(request):
    text = request.data.get('text',None)
    if text is not None:
        pets = Pet.objects.filter(Q(type__icontains= text)|Q(breed__icontains= text)|Q(gender__icontains= text)|Q(name__icontains= text))
    else:
        pets= Pet.objects.all()
    response = []
    for pet in pets:
        username = pet.user.username
        post = BreedingPost.objects.filter(pet = pet)
        if not post:
            continue
        post = post[0]
        serialized_pet = PetSerializer(pet).data
        holder = serialized_pet

        photo = None
        if pet.photo :
            photo = f"{settings.DOMAIN}{pet.photo.url}"

        holder.update({"photo":photo})
        holder.update({"username":username})
        holder.update({"details":post.details})
        holder.update({"id":post.id})
        holder.update({"logo":post.user.user_photo})

        response.append(holder)
    return Response(response, status= status.HTTP_200_OK)