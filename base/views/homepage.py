from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..models import AdoptionPost, BreedingPost , Product, Pet
from django.contrib.auth import get_user_model
from django.conf import settings
from ..serializers import HomepageAdoptionPostSerializer , HomepageBreedingPostSerializer ,HomepageProductSerializer

User = get_user_model()
from rest_framework import status

@api_view(['GET'])
def get_homepage(request):
    adoption_posts = AdoptionPost.objects.select_related('pet').all()[:10]
    breeding_posts = BreedingPost.objects.select_related('pet').all()[:10]
    products = Product.objects.all().order_by('price')[:10]

    response = {
        'adoption_posts': HomepageAdoptionPostSerializer(adoption_posts, many=True).data,
        'breeding_posts': HomepageBreedingPostSerializer(breeding_posts, many=True).data,
        'store': HomepageProductSerializer(products, many=True).data
    }
    return Response(response, status=status.HTTP_200_OK)
