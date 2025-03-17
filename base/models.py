from django.db import models
from django.contrib.auth.models import User

class Pet (models.Model):
    gender_choices = [
        ('male', 'male'),
        ('female', 'female'),
    ]
    type_choices = [
        ('cat', 'cat'),
        ('dog', 'dog'),
    ]
    name = models.TextField(max_length=20)
    gender = models.CharField(
        max_length=6,
        choices=gender_choices
    )
    birth_date = models.DateField(null= True)
    breed = models.TextField(max_length=30 , default='unknown')
    photo = models.ImageField(null=True , blank=True , upload_to='images/')
    type = models.CharField(
        max_length=3,
        choices=type_choices
    )
    user = models.ForeignKey(User , on_delete=models.CASCADE)


class CatVaccination (models.Model):
    feline_panleukopenia_virus = models.BooleanField(default=False)
    feline_herpes_virus = models.BooleanField(default=False)
    feline_calicivirus = models.BooleanField(default=False)
    chlamydophila_felis = models.BooleanField(default=False)
    feline_leukemia_virus = models.BooleanField(default=False)
    feline_immunodeficiency_virus = models.BooleanField(default=False)
    pet = models.ForeignKey(Pet , on_delete=models.CASCADE)

class DogVaccination (models.Model):
    canine_adenovirus_2 = models.BooleanField(default=False)
    canine_distemper_virus = models.BooleanField(default=False)
    canine_parainfluenza_virus = models.BooleanField(default=False)
    canine_parvovirus = models.BooleanField(default=False)
    leptospira_species = models.BooleanField(default=False)
    rabies_virus = models.BooleanField(default=False)
    pet = models.ForeignKey(Pet , on_delete=models.CASCADE)


class AdoptionPost(models.Model):
    details = models.TextField(max_length=100 , null = True , blank = True)
    pet = models.ForeignKey(Pet , on_delete=models.CASCADE)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    photo = models.ImageField(null=True , blank=True , upload_to='images/')

class BreedingPost(models.Model):
    details = models.TextField(max_length=100 , null = True , blank = True)
    pet = models.ForeignKey(Pet , on_delete=models.CASCADE)
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    photo = models.ImageField(null=True , blank=True , upload_to='images/')


class Product(models.Model):
    product_choices = [
        ('toys', 'toys'),
        ('food', 'food'),
        ('clothes', 'clothes'),
    ]
    name = models.CharField(max_length=30)
    price = models.IntegerField(default=0)
    category = models.CharField(
        max_length=7,
        choices=product_choices
    )
    details = models.TextField(max_length=100)
    shipping = models.BooleanField()
    user = models.ForeignKey(User , on_delete=models.CASCADE)
    photo = models.ImageField(null=True , blank=True , upload_to='images/')


