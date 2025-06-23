from django.contrib import admin
from .models import CatVaccination , DogVaccination , Pet , AdoptionPost , BreedingPost , Product

admin.site.register(Pet)
admin.site.register(CatVaccination)
admin.site.register(DogVaccination)
admin.site.register(AdoptionPost)
admin.site.register(BreedingPost)
admin.site.register(Product)
