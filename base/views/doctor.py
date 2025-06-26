from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import DoctorSerializer
from ..models import Doctor
from rest_framework import status
from PIL import Image
import os
from django.contrib.auth.models import User

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def join_as_doctor (request):
    user = request.user
    obj = DoctorSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        obj.update({ "user" : user }) 
        certificate_image = request.FILES.get('certificate_image')
        #obj.pop('certificate_image')
        doctor = Doctor.objects.create(**obj)# , certificate_image = certificate_image)
        return Response(DoctorSerializer(doctor).data , status=status.HTTP_201_CREATED )
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)