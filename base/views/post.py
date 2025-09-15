import datetime
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , AdoptionPost , BreedingPost
from django.contrib.auth import get_user_model

User = get_user_model()
from ..serializers import PetSerializer, AdoptionPostWriteSerializer , AdoptionPostReadSerializer
from rest_framework import status
from django.db.models import Q
from django.conf import settings
from rest_framework import generics, permissions, serializers
from django.shortcuts import get_object_or_404

# List all adoption posts (public)
class AdoptionPostListView(generics.ListAPIView):
    queryset = AdoptionPost.objects.select_related('pet', 'user').all()
    serializer_class = AdoptionPostReadSerializer
    permission_classes = []  

# Retrieve a single adoption post (public)
class AdoptionPostDetailView(generics.RetrieveAPIView):
    queryset = AdoptionPost.objects.select_related('pet', 'user').all()
    serializer_class = AdoptionPostReadSerializer
    permission_classes = []  
    lookup_field = 'id'

# Create a new adoption post (auth required)
class AdoptionPostCreateView(generics.CreateAPIView):
    serializer_class = AdoptionPostWriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        pet = get_object_or_404(Pet, id=self.kwargs['id'])
        if AdoptionPost.objects.filter(pet=pet).exists():
            raise serializers.ValidationError({"message": "pet adoption post already exists"})
        serializer.save(user=self.request.user, pet=pet)

# Delete an adoption post (auth + ownership required)
class AdoptionPostDeleteView(generics.DestroyAPIView):
    queryset = AdoptionPost.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            self.permission_denied(self.request, message="user does not have this post")
        instance.delete()


from rest_framework.views import APIView
from django.utils.dateparse import parse_date


class AdoptionPostFilterView(APIView):
    permission_classes = []  

    def post(self, request):
        data = request.data
        filter_params = {
            'pet__type': data.get('type'),
            'pet__breed': data.get('breed'),
            'pet__gender': data.get('gender'),
        }

        country = data.get('country')
        if country:
            filter_params['user__country'] = country

        birth_date = data.get('age')
        if birth_date:
            birth_date_obj = parse_date(birth_date)
            if not birth_date_obj:
                return Response(
                    {"message": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            filter_params['pet__birth_date__gte'] = birth_date_obj

        filter_params = {k: v for k, v in filter_params.items() if v is not None}

        posts = (
            AdoptionPost.objects
            .select_related('pet', 'user')
            .filter(**filter_params)
            .order_by('pet__birth_date')
        )

        serializer = AdoptionPostReadSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdoptionPostSearchView(APIView):
    permission_classes = []  # Public

    def post(self, request):
        text = request.data.get('text')
        pet_filter = Q()
        if text:
            pet_filter = (
                Q(pet__type__icontains=text) |
                Q(pet__breed__icontains=text) |
                Q(pet__gender__icontains=text) |
                Q(pet__name__icontains=text)
            )

        posts = (
            AdoptionPost.objects
            .select_related('pet', 'user')
            .filter(pet_filter)
        )

        serializer = AdoptionPostReadSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
#############################################################################################

from ..serializers import BreedingPostReadSerializer, BreedingPostWriteSerializer

# List all breeding posts (public)
class BreedingPostListView(generics.ListAPIView):
    queryset = BreedingPost.objects.select_related('pet', 'user').all()
    serializer_class = BreedingPostReadSerializer
    permission_classes = []  

# Retrieve a single breeding post (public)
class BreedingPostDetailView(generics.RetrieveAPIView):
    queryset = BreedingPost.objects.select_related('pet', 'user').all()
    serializer_class = BreedingPostReadSerializer
    permission_classes = []  
    lookup_field = 'id'

# Create a new breeding post (auth required)
class BreedingPostCreateView(generics.CreateAPIView):
    serializer_class = BreedingPostWriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        pet = get_object_or_404(Pet, id=self.kwargs['id'])
        if BreedingPost.objects.filter(pet=pet).exists():
            raise serializers.ValidationError({"message": "pet breeding post already exists"})
        serializer.save(user=self.request.user, pet=pet)

# Delete a breeding post (auth + ownership required)
class BreedingPostDeleteView(generics.DestroyAPIView):
    queryset = BreedingPost.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            self.permission_denied(self.request, message="user does not have this post")
        instance.delete()

from rest_framework.views import APIView

class BreedingPostFilterView(APIView):
    permission_classes = []  

    def post(self, request):
        data = request.data
        filter_params = {
            'pet__type': data.get('type'),
            'pet__breed': data.get('breed'),
            'pet__gender': data.get('gender'),
        }

        country = data.get('country')
        if country:
            filter_params['user__country'] = country

        birth_date = data.get('age')
        if birth_date:
            birth_date_obj = parse_date(birth_date)
            if not birth_date_obj:
                return Response(
                    {"message": "Invalid date format. Use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            filter_params['pet__birth_date__gte'] = birth_date_obj

        filter_params = {k: v for k, v in filter_params.items() if v is not None}

        posts = (
            BreedingPost.objects
            .select_related('pet', 'user')
            .filter(**filter_params)
            .order_by('pet__birth_date')
        )

        serializer = BreedingPostReadSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# Search breeding posts
class BreedingPostSearchView(APIView):
    permission_classes = []  

    def post(self, request):
        text = request.data.get('text')
        pet_filter = Q()
        if text:
            pet_filter = (
                Q(pet__type__icontains=text) |
                Q(pet__breed__icontains=text) |
                Q(pet__gender__icontains=text) |
                Q(pet__name__icontains=text)
            )

        posts = (
            BreedingPost.objects
            .select_related('pet', 'user')
            .filter(pet_filter)
        )

        serializer = BreedingPostReadSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)