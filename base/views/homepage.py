from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import AdoptionPost, BreedingPost , Product
from django.contrib.auth import get_user_model

User = get_user_model()
from ..serializers import AdoptionPostSerializer, BreedingPostSerializer, ProductSerializer
from rest_framework import status

@api_view(['GET'])
def get_homepage (request):
    adoption_posts = AdoptionPost.objects.all()[:10]
    adoption_posts = AdoptionPostSerializer(adoption_posts, many = True).data
    breeding_posts = BreedingPost.objects.all()[:10]
    breeding_posts = BreedingPostSerializer(breeding_posts, many = True).data
    products = Product.objects.all().order_by('price')[:10]
    products = ProductSerializer(products, many = True).data
    response = {'adoption_posts':adoption_posts}
    response.update({'breeding_posts':breeding_posts})
    response.update({'products':products})
    return Response (response, status= status.HTTP_200_OK)
