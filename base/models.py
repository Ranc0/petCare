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
    user = models.ForeignKey(User , on_delete=models.CASCADE,null=True, blank=True)
    photo = models.ImageField(null=True , blank=True , upload_to='images/')


class Store(models.Model):
    store_name = models.CharField(max_length=30)
    location = models.CharField(null = True,max_length=500)
    logo = models.ImageField(null=True, blank=True, upload_to='images/')
    user = models.OneToOneField(User, on_delete= models.CASCADE)

    def delete(self, *args, **kwargs):
        # Delete the Doctor instance without deleting the associated User
        self.user = None
        super().delete(*args, **kwargs)

class Doctor(models.Model):
    certificate_image = models.ImageField(null = True, blank  =True, upload_to = 'images/')
    experience = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete= models.CASCADE)

    def delete(self, *args, **kwargs):
        self.user = None
        super().delete(*args, **kwargs)

class DoctorPost(models.Model):
    post_title = models.CharField(null = True, max_length=200)
    post = models.CharField(null = True, max_length=1000)
    date = models.DateField(null = True, auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class UserPhoto(models.Model):
    user_photo = models.ImageField(null = True, blank  =True, upload_to = 'images/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)