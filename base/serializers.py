from rest_framework import serializers
from .models import Pet , CatVaccination , DogVaccination , AdoptionPost
from django.contrib.auth.models import User

class PetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pet
        exclude = ('user',)

class CatVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatVaccination
        exclude = ('pet',)

class DogVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogVaccination
        exclude = ('pet',)

class AdoptionPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionPost
        exclude = ('user','pet',)
