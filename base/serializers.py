from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from datetime import date
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = PendingUser
        fields = [
            'username', 'email', 'password', 'confirm_password',
            'first_name', 'last_name', 'country'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists() or PendingUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email exists")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists() or PendingUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username exists")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        # Hash password if needed
        validated_data['password'] = make_password(validated_data['password'])
        return PendingUser.objects.create(**validated_data)
from rest_framework import serializers
from django.conf import settings
from datetime import date
from .models import Pet, AdoptionPost, BreedingPost


class PetSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()

    class Meta:
        model = Pet
        exclude = ('user',)  # keep 'photo' so it's writable

    def get_age(self, obj):
        if obj.birth_date:
            return (date.today() - obj.birth_date).days
        return None

    def to_representation(self, instance):
        """Keep photo writable but return full URL in responses."""
        rep = super().to_representation(instance)
        request = self.context.get('request')
        if instance.photo:
           rep['photo'] = f"{settings.DOMAIN}{instance.photo.url}"
        return rep


from rest_framework import serializers
from django.conf import settings
from .models import AdoptionPost, BreedingPost


class HomepageAdoptionPostSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = AdoptionPost
        exclude = ('user',)  # user will be set from request, not client

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.photo:
            rep['photo'] = f"{settings.DOMAIN}{instance.photo.url}"
        else:
            rep['photo'] = None
        return rep


class HomepageBreedingPostSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = BreedingPost
        exclude = ('user',)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.photo:
            rep['photo'] = f"{settings.DOMAIN}{instance.photo.url}"
        else:
            rep['photo'] = None
        return rep


class CatVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatVaccination
        exclude = ('pet',)

class DogVaccinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DogVaccination
        exclude = ('pet',)


class ProductReadSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    store_id = serializers.SerializerMethodField()
    store_name = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    country = serializers.CharField(source='user.country', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'price', 'category', 'details', 'shipping',
            'photo', 'store_id', 'store_name', 'logo', 'country'
        ]

    def get_photo(self, obj):
        return f"{settings.DOMAIN}{obj.photo.url}" if obj.photo else None

    def get_store_id(self, obj):
        store = getattr(obj.user, 'store', None)
        return store.id if store else None

    def get_store_name(self, obj):
        store = getattr(obj.user, 'store', None)
        return store.store_name if store else None

    def get_logo(self, obj):
        store = getattr(obj.user, 'store', None)
        return f"{settings.DOMAIN}{store.logo.url}" if store and store.logo else None


class ProductWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'details', 'shipping', 'photo']

class StoreReadSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()

    class Meta:
        model = Store
        fields = ['id', 'store_name', 'logo', 'products']

    def get_logo(self, obj):
        return f"{settings.DOMAIN}{obj.logo.url}" if obj.logo else None

    def get_products(self, obj):
        products = Product.objects.filter(user=obj.user)
        data = []
        for product in products:
            product_data = ProductReadSerializer(product).data
            product_data['photo'] = (
                f"{settings.DOMAIN}{product.photo.url}" if product.photo else None
            )
            data.append(product_data)
        return data


class StoreWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['store_name']  # logo handled separately, user set in view



class DoctorSerializer(serializers.ModelSerializer):
    certificate_image = serializers.ImageField(write_only=True, required=True, allow_null=False)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_photo = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        exclude = ('user',)  # user set in view

    def get_first_name(self, obj):
        return f"Dr. {obj.user.first_name}" if obj.user and obj.user.first_name else None

    def get_user_photo(self, obj):
        if obj.user and obj.user.user_photo:
            return f"{settings.DOMAIN}{obj.user.user_photo.url}"
        return None


class DoctorPostSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    logo = serializers.SerializerMethodField()

    class Meta:
        model = DoctorPost
        exclude = ('user',)  # user will be set in the view

    def get_logo(self, obj):
        if obj.user and obj.user.user_photo:
            return f"{settings.DOMAIN}{obj.user.user_photo.url}"
        return None
    
from rest_framework import serializers
from django.conf import settings
from .models import Product, AdoptionPost, BreedingPost

class HomepageProductSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'photo', 'name', 'price')

    def get_photo(self, obj):
        return f"{settings.DOMAIN}{obj.photo.url}" if obj.photo else None



from datetime import date
from rest_framework import serializers
from django.conf import settings
from .models import AdoptionPost

class AdoptionPostReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='pet.name', read_only=True)
    gender = serializers.CharField(source='pet.gender', read_only=True)
    photo = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    country = serializers.CharField(source='user.country', read_only=True)
    logo = serializers.SerializerMethodField()
    breed = serializers.CharField(source='pet.breed', read_only=True)
    type = serializers.CharField(source='pet.type', read_only=True)
    birth_date = serializers.DateField(source='pet.birth_date', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = AdoptionPost
        fields = [
            'id', 'details', 'created_at',
            'name', 'gender', 'breed', 'type',
            'birth_date', 'age', 'photo',
            'username', 'country', 'logo'
        ]

    def get_photo(self, obj):
        return f"{settings.DOMAIN}{obj.pet.photo.url}" if obj.pet and obj.pet.photo else None

    def get_logo(self, obj):
        return f"{settings.DOMAIN}{obj.user.user_photo.url}" if obj.user and obj.user.user_photo else None

    def get_age(self, obj):
        if obj.pet and obj.pet.birth_date:
            return (date.today() - obj.pet.birth_date).days
        return None


    def get_pet_photo(self, obj):
        return f"{settings.DOMAIN}{obj.pet.photo.url}" if obj.pet and obj.pet.photo else None

    def get_logo(self, obj):
        return f"{settings.DOMAIN}{obj.user.user_photo.url}" if obj.user and obj.user.user_photo else None

class AdoptionPostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoptionPost
        fields = ['details']

class BreedingPostReadSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='pet.name', read_only=True)
    gender = serializers.CharField(source='pet.gender', read_only=True)
    photo = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    country = serializers.CharField(source='user.country', read_only=True)
    logo = serializers.SerializerMethodField()
    breed = serializers.CharField(source='pet.breed', read_only=True)
    type = serializers.CharField(source='pet.type', read_only=True)
    birth_date = serializers.DateField(source='pet.birth_date', read_only=True)
    age = serializers.SerializerMethodField()

    class Meta:
        model = BreedingPost
        fields = [
            'id', 'details', 'created_at',
            'name', 'gender', 'breed', 'type',
            'birth_date', 'age', 'photo',
            'username', 'country', 'logo'
        ]

    def get_photo(self, obj):
        return f"{settings.DOMAIN}{obj.pet.photo.url}" if obj.pet and obj.pet.photo else None

    def get_logo(self, obj):
        return f"{settings.DOMAIN}{obj.user.user_photo.url}" if obj.user and obj.user.user_photo else None

    def get_age(self, obj):
        if obj.pet and obj.pet.birth_date:
            return (date.today() - obj.pet.birth_date).days
        return None


class BreedingPostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreedingPost
        fields = ['details']
  
