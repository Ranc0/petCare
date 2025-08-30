from rest_framework import serializers
from .models import Pet , CatVaccination , DogVaccination , AdoptionPost , BreedingPost , Product, Store, Doctor, DoctorPost
from django.contrib.auth.models import User
from datetime import date

class PetSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        exclude = ('user', 'photo')

    def get_age(self, obj):
        if obj.birth_date:
            return (date.today() - obj.birth_date).days
        return None




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
        exclude = ('user','certificate_image')

class DoctorPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorPost
        exclude = ('user',)
