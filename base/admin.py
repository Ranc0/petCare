from django.contrib import admin
from .models import CatVaccination , DogVaccination , Pet , AdoptionPost , BreedingPost , Product, Store, Doctor, DoctorPost, UserPhoto

admin.site.register(Pet)
admin.site.register(CatVaccination)
admin.site.register(DogVaccination)
admin.site.register(AdoptionPost)
admin.site.register(BreedingPost)
admin.site.register(Product)
admin.site.register(Store)
admin.site.register(Doctor)
admin.site.register(DoctorPost)
admin.site.register(UserPhoto)
