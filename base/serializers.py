from rest_framework import serializers
from .models import Pet , CatVaccination , DogVaccination , AdoptionPost , BreedingPost , Product, Store, Doctor
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
        exclude = ('user','pet','photo')

class BreedingPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedingPost
        exclude = ('user','pet','photo')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        exclude = ('user','photo',)

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        exclude = ('user','logo')

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        excluse = ('user','certificate_image')
