from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.urls import path
from .views import *
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
    path('pet/add', PetListCreateView.as_view(), name='add_pet'),
    path('pet/get_user_pets', PetListCreateView.as_view(), name='get_user_pets'),
    path('pet/get/<str:pk>', PetRetrieveUpdateDestroyView.as_view(), name='get_pet'),
    path('pet/update/<str:pk>', PetRetrieveUpdateDestroyView.as_view(), name='update_pet'),
    path('pet/delete/<str:pk>', PetRetrieveUpdateDestroyView.as_view(), name='delete_pet'),
    path ('pet/update_photo/<str:id>' , views.pet.update_pet_photo, name = 'update_pet_photo'),
    path('pet/get/vaccinations/<str:id>',VaccinationRetrieveUpdateView.as_view(), name='get_vaccinations'),
    path('pet/update/vaccinations/<str:id>', VaccinationRetrieveUpdateView.as_view(),name='update_vaccinations'),
    #####
    #path('vaccination/dog/update/<str:id>' , views.vaccination.update_dog_vaccination, name = 'update_dog_vaccination'),
    #path('vaccination/cat/update/<str:id>' , views.vaccination.update_cat_vaccination, name = 'update_cat_vaccination'),

    #####
    path('post/adoption/add/<int:id>', AdoptionPostCreateView.as_view(), name='add_adoption_post'),
    path('post/adoption/delete/<int:id>', AdoptionPostDeleteView.as_view(), name='delete_adoption_post'),
    path('post/adoption/get', AdoptionPostListView.as_view(), name='get_adoption_posts'),
    path('post/adoption/get/<int:id>', AdoptionPostDetailView.as_view(), name='get_adoption_post'),
    path('post/adoption/filter', AdoptionPostFilterView.as_view(), name='adoption_filter'),
    path('post/adoption/search', AdoptionPostSearchView.as_view(), name='adoption_post_search'),

    path('post/breeding/add/<int:id>', BreedingPostCreateView.as_view(), name='add_breeding_post'),
    path('post/breeding/delete/<int:id>', BreedingPostDeleteView.as_view(), name='delete_breeding_post'),
    path('post/breeding/get', BreedingPostListView.as_view(), name='get_breeding_posts'),
    path('post/breeding/get/<int:id>', BreedingPostDetailView.as_view(), name='get_breeding_post'),
    path('post/breeding/filter', BreedingPostFilterView.as_view(), name='breeding_filter'),
    path('post/breeding/search', BreedingPostSearchView.as_view(), name='breeding_post_search'),

    #####
    path('product/add', ProductCreateView.as_view(), name='add_product'),
    path('product/delete/<int:id>', ProductDeleteView.as_view(), name='delete_product'),
    path('product/get', ProductListView.as_view(), name='get_products'),
    path('product/get/<int:id>', ProductDetailView.as_view(), name='get_product'),
    path('product/filter', ProductFilterView.as_view(), name='product_filter'),
    path('product/search', ProductSearchView.as_view(), name='product_search'),
    path('product/update/<int:id>', UpdateProductPhotoView.as_view(), name='update_product_photo'),

    #####
    path('store/create', StoreCreateView.as_view(), name='create_store'),
    path('store/get/<int:id>', StoreDetailView.as_view(), name='get_store'),
    path('store/delete/<int:id>', StoreDeleteView.as_view(), name='delete_store'),
    path('store/update/<int:id>', StoreUpdateLogoView.as_view(), name='update_store_photo'),

    ######
    path('doctor/join', views.doctor.join_as_doctor, name = 'join_as_doctor'),
    path('doctor/update_certificate_image/<str:id>', views.doctor.update_certificate_photo, name = 'update_certificate_photo'),
    path('doctor/add_post', views.doctor.add_post, name = 'add_post'),
    path('doctor/get_posts', views.doctor.get_posts, name = 'get_posts'),
    path('doctor/get_doctors', views.doctor.get_doctors, name = 'get_doctors'),

    ######
    path('ai/vision/dog', views.vision_ai.dog_vision, name = 'dog-skin'),
    path('ai/vision/cat', views.vision_ai.cat_vision, name = 'cat-skin'),
    path('ai/dog', views.ai.dog, name = 'dog'),
    path('ai/cat', views.ai.cat, name = 'cat'),

]