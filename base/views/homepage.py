from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..models import AdoptionPost, BreedingPost , Product, Pet
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
from rest_framework import status

@api_view(['GET'])
def get_homepage (request):
    response = {'adoption_posts':[], 'breeding_posts':[], 'store':[]}

    adoption_posts = AdoptionPost.objects.all()[:10]
    breeding_posts = BreedingPost.objects.all()[:10]
    products = Product.objects.all().order_by('price')[:10]

    for post in adoption_posts:
        holder = {}
        pet = Pet.objects.get(id = post.pet_id)
        photo = None
        if pet.photo :
            photo = f"{settings.DOMAIN}{pet.photo.url}"
        holder.update({"id":post.id})
        holder.update({"photo":photo})
        holder.update({"name":pet.name})
        holder.update({"gender":pet.gender})
        response['adoption_posts'].append(holder)

    for post in breeding_posts:
        holder = {}
        pet = Pet.objects.get(id = post.pet_id)
        photo = None
        if pet.photo :
            photo = f"{settings.DOMAIN}{pet.photo.url}"
        holder.update({"id":post.id})
        holder.update({"photo":photo})
        holder.update({"name":pet.name})
        holder.update({"gender":pet.gender})
        response['breeding_posts'].append(holder)

    for product in products:
        holder = {}
        photo = None
        if product.photo :
            photo = f"{settings.DOMAIN}{product.photo.url}"
        holder.update({"id":product.id})
        holder.update({"photo":photo})
        holder.update({"name":product.name})
        holder.update({"price":product.price})
        response['store'].append(holder)
    return Response (response, status= status.HTTP_200_OK)
