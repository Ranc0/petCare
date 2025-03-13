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
    #####
    path ('pet/add' , views.pet.add_pet, name = 'add_pet'),

    #####
    path('vaccination/dog/update/<str:id>' , views.vaccination.update_dog_vaccination, name = 'update_dog_vaccination'),
    path('vaccination/cat/update/<str:id>' , views.vaccination.update_cat_vaccination, name = 'update_cat_vaccination'),

    #####
    path ('post/adoption/add/<str:id>', views.post.add_adoption_post , name = 'add_adoption_post')

]