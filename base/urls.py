from django.urls import path 
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    #####
    path('',views.index , name='index'),
    #####
    path('homepage', views.homepage , name = 'homepage'),
    
    #####
    path('account/sign_in' ,views.account.sign_in , name = 'sign_in' ),
    path('account/sign_up' ,views.account.sign_up , name = 'sign_up' ),
    #####
    path ('pet/add' , views.pet.add_pet, name = 'add_pet'),
    path ('pet/update/<str:id>' , views.pet.update_pet, name = 'update_pet'),
    path ('pet/get/<str:id>' , views.pet.get_pet, name = 'get_pet'),
    path ('pet/delete/<str:id>' , views.pet.delete_pet, name = 'delete_pet'),
    path ('pet/update_photo/<str:id>' , views.pet.update_pet_photo, name = 'update_pet_photo'),

    #####
    path('vaccination/dog/update/<str:id>' , views.vaccination.update_dog_vaccination, name = 'update_dog_vaccination'),
    path('vaccination/cat/update/<str:id>' , views.vaccination.update_cat_vaccination, name = 'update_cat_vaccination'),

    #####
    path ('post/adoption/add/<str:id>', views.post.add_adoption_post , name = 'add_adoption_post'),
    path ('post/adoption/delete/<str:id>', views.post.delete_adoption_post , name = 'delete_adoption_post'),
    path ('post/adoption/get/<str:id>', views.post.get_adoption_post , name = 'get_adoption_post'),
    path ('post/adoption/get', views.post.get_adoption_posts , name = 'get_adoption_posts'),
    path ('post/adoption/filter', views.post.adoption_filter , name = 'doption_filter'),

    #####
    path('product/add' , views.product.add_product, name = 'add_product'),
    path('product/delete/<str:id>' , views.product.delete_product, name = 'delete_product'),
    path('product/get', views.product.get_products, name = 'get_products'),
    path('product/get/<str:id>', views.get_product, name = 'get_product'),
    path('product/filter', views.product_filter, name = 'product_filter'),

]