from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import PetSerializer, CatVaccinationSerializer, DogVaccinationSerializer
from ..models import Pet , CatVaccination , DogVaccination
from rest_framework import status
from PIL import Image
import os
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()

from rest_framework import generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class PetListCreateView(generics.ListCreateAPIView):
    serializer_class = PetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return pets belonging to the logged-in user
        return Pet.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        pet = serializer.save(user=self.request.user)
        # Auto-create vaccination record
        if pet.type == 'cat':
            CatVaccination.objects.create(pet=pet)
        else:
            DogVaccination.objects.create(pet=pet)


class PetRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PetSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return []  # No authentication required for GET
        return [permissions.IsAuthenticated()]  # Auth required for PUT/DELETE

    def get_queryset(self):
        if self.request.method == 'GET':
            return Pet.objects.all()  # Allow public access to any pet
        return Pet.objects.filter(user=self.request.user)  # Restrict updates/deletes


@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_pet_photo(request, id):
    pet = get_object_or_404(Pet, id=id)
    if pet.user != request.user:
        return Response({"message": "You do not own this pet"}, status=status.HTTP_403_FORBIDDEN)

    photo = request.FILES.get('photo')
    if not photo:
        return Response({"message": "photo is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate image
        image = Image.open(photo)
        image.verify()
        photo.seek(0)  

        # Delete old photo if exists
        if pet.photo and os.path.isfile(pet.photo.path):
            os.remove(pet.photo.path)

        # Save new photo
        pet.photo = photo
        pet.save()

        # Serialize updated pet
        response = PetSerializer(pet, context={'request': request}).data
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)

class VaccinationRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_pet(self):
        pet = get_object_or_404(Pet, id=self.kwargs['id'])
        if pet.user != self.request.user:
            self.permission_denied(self.request, message="user does not have the pet")
        return pet

    def get_object(self):
        pet = self.get_pet()
        if pet.type == 'cat':
            return get_object_or_404(CatVaccination, pet=pet)
        elif pet.type == 'dog':
            return get_object_or_404(DogVaccination, pet=pet)
        else:
            self.permission_denied(self.request, message="Unknown pet type")

    def get_serializer_class(self):
        pet = self.get_pet()
        return CatVaccinationSerializer if pet.type == 'cat' else DogVaccinationSerializer


