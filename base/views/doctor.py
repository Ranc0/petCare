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
def join_as_doctor(request):
    user = request.user
    if Doctor.objects.filter(user = user):
        return Response({"message": "you are already a doctor"}, status=status.HTTP_409_CONFLICT)
    serializer = DoctorSerializer(data=request.data)
    if serializer.is_valid():
        doctor = serializer.save(user=user, certificate_image=None)
        return Response(
            DoctorSerializer(doctor).data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"message": "form is not valid", "errors": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


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
    get_object_or_404(Doctor, user=user)  # ensures only doctors can post

    serializer = DoctorPostSerializer(data=request.data)
    if serializer.is_valid():
        doctor_post = serializer.save(user=user)
        return Response(
            DoctorPostSerializer(doctor_post).data,
            status=status.HTTP_201_CREATED
        )
    return Response(
        {"message": serializer.errors},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(["GET"])
def get_posts(request):
    posts = DoctorPost.objects.all()
    return Response({"posts": DoctorPostSerializer(posts, many=True).data})

@api_view(["GET"])
def get_doctors(request):
    doctors = Doctor.objects.all()
    return Response(DoctorSerializer(doctors, many=True).data)


