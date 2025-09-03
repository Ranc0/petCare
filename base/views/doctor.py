from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..serializers import DoctorSerializer, DoctorPostSerializer
from ..models import Doctor, DoctorPost
from rest_framework import status
from PIL import Image
import os
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def join_as_doctor (request):
    user = request.user
    obj = DoctorSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        obj.update({ "user" : user })
        doctor = Doctor.objects.create(**obj, certificate_image = None)
        #DoctorSerializer(doctor).data
        return Response("user joined as doctor succesfully" , status=status.HTTP_201_CREATED )
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)

@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_certificate_photo(request, id):
    user = get_object_or_404(User, id = id)
    doctor = get_object_or_404(Doctor, user = user)
    certificate_image = request.FILES.get('certificate_image')
    if not certificate_image:
        return Response({"message": "certificate image is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate the uploaded file as an image
        image = Image.open(certificate_image)
        image.verify()  # Verify the image integrity

        # Delete the old photo if it exists
        if doctor.certificate_image and os.path.isfile(doctor.certificate_image.path):
            os.remove(doctor.certificate_image.path)

        # Update the photo field
        doctor.certificate_image = certificate_image
        doctor.save()

        # Serialize
        image = None
        if doctor.certificate_image :
            image = f"{settings.DOMAIN}{doctor.certificate_image.url}"
        response = {"certificate_image": image}
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def add_post(request):
    user = request.user
    doctor = get_object_or_404(Doctor, user = user)
    obj = DoctorPostSerializer(data = request.data, many = False)
    if (obj.is_valid()):
        obj = obj.data
        obj.update({ "user" : user })
        doctor_post = DoctorPost.objects.create(**obj)
        return Response(DoctorPostSerializer(doctor_post).data , status=status.HTTP_201_CREATED )
    return Response({"message":"form is not valid"} , status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_posts(request):
    holder = []
    posts = DoctorPost.objects.all()
    for post in posts:
        user_photo = None
        if post.user.user_photo:
            user_photo = f"{settings.DOMAIN}{post.user.user_photo}"
        post_serialized = DoctorPostSerializer(post).data
        post_serialized.update({"logo":user_photo})
        post_serialized.update({"first_name" : post.user.first_name})
        post_serialized.update({"last_name" : post.user.last_name})
        holder.append(post_serialized)
    response = {"posts":holder}
    return Response(response, status= status.HTTP_200_OK)

@api_view(["GET"])
def get_doctors(request):
    response = []
    doctors = Doctor.objects.all()
    for doctor in doctors:
        user = doctor.user
        holder = {}
        user_photo = None
        if user.user_photo:
            user_photo = f"{settings.DOMAIN}{user.user_photo}"
        holder.update({"first_name":"Dr." + user.first_name})
        holder.update({"photo":user_photo})
        holder.update({"experience":doctor.experience})
        holder.update({"details":doctor.details})
        posts = []
        query = DoctorPost.objects.filter(user = user)
        for post in query:
            posts.append(DoctorPostSerializer(post).data)
        holder.update({"posts" : posts})
        response.append(holder)
    return Response(response, status = status.HTTP_200_OK)