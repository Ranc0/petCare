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
    path('account/sign_in' ,views.account.sign_in , name = 'sign_in' ),
    path('account/sign_up' ,views.account.sign_up , name = 'sign_up' ),
    path('account/get_account/<str:id>', views.account.get_account, name = 'get_account'),
    path('account/update_user_photo/<str:id>', views.account.update_user_photo, name = 'update_user_photo'),

    path('account/verify_otp/sign_up', views.account.verify_otp, name='verify_otp_sign_up'),
    path('account/verify_otp/forgot_password', views.account.verify_otp, name='verify_otp_forgot_password'),
    path('account/resend_code', views.account.resend_otp, name='resend_otp' ),
    path('account/forgot_password',views.account.forgot_password, name = 'forgot_password'),
    path('account/reset_password/<str:id>', views.account.reset_password, name = 'reset_password'),

    #####
    path('homepage', views.homepage.get_homepage, name = 'homepage' ),

    #####
    path ('pet/add' , views.pet.add_pet, name = 'add_pet'),
    path ('pet/update/<str:id>' , views.pet.update_pet, name = 'update_pet'),
    path ('pet/get/<str:id>' , views.pet.get_pet, name = 'get_pet'),
    path ('pet/get_user_pets', views.pet.get_user_pets, name = 'get_user_pets'),
    path ('pet/delete/<str:id>' , views.pet.delete_pet, name = 'delete_pet'),
    path ('pet/update_photo/<str:id>' , views.pet.update_pet_photo, name = 'update_pet_photo'),
    path ('pet/get/vaccinations/<str:id>', views.pet.get_vaccinations, name = 'get_vaccinations'),
    path ('pet/update/vaccinations/<str:id>', views.pet.update_vaccinations, name = 'update_vaccinations'),

    #####
    #path('vaccination/dog/update/<str:id>' , views.vaccination.update_dog_vaccination, name = 'update_dog_vaccination'),
    #path('vaccination/cat/update/<str:id>' , views.vaccination.update_cat_vaccination, name = 'update_cat_vaccination'),

    #####
    path ('post/adoption/add/<str:id>', views.post.add_adoption_post , name = 'add_adoption_post'),
    path ('post/adoption/delete/<str:id>', views.post.delete_adoption_post , name = 'delete_adoption_post'),
    path ('post/adoption/get/<str:id>', views.post.get_adoption_post , name = 'get_adoption_post'),
    path ('post/adoption/get', views.post.get_adoption_posts , name = 'get_adoption_posts'),
    path ('post/adoption/filter', views.post.adoption_filter , name = 'doption_filter'),
    path ('post/adoption/search', views.post.adoption_post_search , name = 'adoption_post_search'),

    path ('post/breeding/add/<str:id>', views.post.add_breeding_post , name = 'add_breeding_post'),
    path ('post/breeding/delete/<str:id>', views.post.delete_breeding_post , name = 'delete_breeding_post'),
    path ('post/breeding/get/<str:id>', views.post.get_breeding_post , name = 'get_breeding_post'),
    path ('post/breeding/get', views.post.get_breeding_posts , name = 'get_breeding_posts'),
    path ('post/breeding/filter', views.post.breeding_filter , name = 'breeding_filter'),
    path ('post/breeding/search', views.post.breeding_post_search , name = 'breeding_post_search'),

    #####
    path('product/add' , views.product.add_product, name = 'add_product'),
    path('product/delete/<str:id>' , views.product.delete_product, name = 'delete_product'),
    path('product/get', views.product.get_products, name = 'get_products'),
    path('product/get/<str:id>', views.product.get_product, name = 'get_product'),
    path('product/filter', views.product.product_filter, name = 'product_filter'),
    path('product/search', views.product.product_search, name = 'product_search'),
    path('product/update/<str:id>', views.product.update_product_photo, name = 'update_product_photo'),

    #####
    path('store/create', views.create_store, name= 'create_store'),
    path('store/delete/<str:id>', views.delete_store, name = 'delete_store'),
    path('store/get/<str:id>', views.get_store, name = 'get_store'),
    path('store/update/<str:id>', views.update_store_photo, name = 'update_store_photo'),

    ######
    path('doctor/join', views.doctor.join_as_doctor, name = 'join_as_doctor'),
    path('doctor/update_certificate_image/<str:id>', views.doctor.update_certificate_photo, name = 'update_certificate_photo'),
    path('doctor/add_post', views.doctor.add_post, name = 'add_post'),
    path('doctor/get_posts', views.doctor.get_posts, name = 'get_posts'),

    ######
    # path('ai/vision/dog', views.vision_ai.dog_vision, name = 'dog-skin'),
    # path('ai/vision/cat', views.vision_ai.cat_vision, name = 'cat-skin'),

]