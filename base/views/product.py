from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , Product
from django.contrib.auth.models import User
from ..serializers import PetSerializer
from rest_framework import status

#views to add :
#add product
#update product
#delete product
#getters (filters must be applied)