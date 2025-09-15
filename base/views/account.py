
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth.models import User
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Doctor, DoctorPost, PendingUser, BreedingPost, AdoptionPost, Pet, Store
from ..serializers import DoctorPostSerializer, PetSerializer , BreedingPostReadSerializer , AdoptionPostReadSerializer
from PIL import Image
import os
from ..utils import *

User = get_user_model()

@api_view(['POST'])
def verify_otp(request):
    user_id = request.data.get('user_id')
    otp = request.data.get('otp')
    if request.path.endswith('/sign_up'):
        request_status = "sign_up"
    elif request.path.endswith('/forgot_password'):
        request_status = "forgot_password"
    else:
        return Response({"error": "Invalid endpoint"}, status=status.HTTP_400_BAD_REQUEST)


    if not user_id or not otp:
        return Response({"error": "user_id and otp are required"},status=status.HTTP_400_BAD_REQUEST)

    is_valid, message, user = handle_otp_verification(user_id, otp, request_status)
    if not is_valid:
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'id' : user.id,
    })

@api_view(['POST'])
def sign_in(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    store_id = None
    query = Store.objects.filter(user = user)
    if query:
        store = query[0]
        store_id = store.id

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username':username ,
        'store_id': store_id ,
        'id':user.id
    })

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..serializers import SignUpSerializer
from ..utils import send_otp_response

@api_view(['POST'])
def sign_up(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        pending_user = serializer.save()
        return send_otp_response(pending_user)
    errors = serializer.errors
    if 'email' in errors:
        return Response({"message": errors['email'][0]}, status=status.HTTP_409_CONFLICT)
    if 'username' in errors:
        return Response({"message": errors['username'][0]}, status=status.HTTP_409_CONFLICT)
    if 'password' in errors:
        return Response({"message": errors['password']}, status=status.HTTP_400_BAD_REQUEST)

    # Fallback for other errors
    return Response({"message": "Invalid input"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    user = get_object_or_404(User, email = email)
    return send_otp_response(user)

@api_view(['POST'])
def resend_otp(request):
    email = request.data.get('email')
    user = get_object_or_404(PendingUser, email = email)
    return send_otp_response(user)

@permission_classes([IsAuthenticated])
@api_view(['POST'])
def reset_password(request, id):
    user = get_object_or_404(User, id = id)
    password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    if password != confirm_password:
        return Response({"message": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(password)
    user.save()
    return Response({"message":"password updated successfully"}, status= status.HTTP_202_ACCEPTED)


@api_view(['GET'])
def get_account(request, id):
    user = get_object_or_404(User, id=id)

    response = {
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "user_photo": (
            f"{settings.DOMAIN}{user.user_photo.url}"
            if user.user_photo else None
        ),
        "country": user.country
    }

    # Doctor-specific data
    doctor = Doctor.objects.filter(user=user).first()
    if doctor:
        response.update({
            "first_name": f"Dr.{user.first_name}",
            "experience": doctor.experience,
            "details": doctor.details,
            "posts": DoctorPostSerializer(
                DoctorPost.objects.filter(user=user),
                many=True,
                context={'request': request}
            ).data
        })

    # Adoption posts
    adoption_posts = AdoptionPost.objects.filter(user_id=id)
    response['adoption_posts'] = AdoptionPostReadSerializer(
        adoption_posts,
        many=True,
        context={'request': request}
    ).data

    # Breeding posts
    breeding_posts = BreedingPost.objects.filter(user_id=id)
    response['breeding_posts'] = BreedingPostReadSerializer(
        breeding_posts,
        many=True,
        context={'request': request}
    ).data

    return Response(response, status=status.HTTP_200_OK)


from PIL import Image, UnidentifiedImageError
@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_user_photo(request, id):
    user = get_object_or_404(User, id=id)

    photo = request.FILES.get("user_photo")
    if not photo:
        return Response({"message": "user photo is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate the uploaded file as an image
        image = Image.open(photo)
        image.verify()  # Verify the image integrity

        # Delete the old photo if it exists
        if user.user_photo:
            user.user_photo.delete(save=False)

        # Update the photo field
        user.user_photo = photo
        user.save()

        # Return URL in your required format
        return Response(
            {
                "user_photo": f"{settings.DOMAIN}{user.user_photo.url}"
                if user.user_photo else None
            },
            status=status.HTTP_200_OK
        )

    except UnidentifiedImageError:
        return Response(
            {"message": "Uploaded file is not a valid image"},
            status=status.HTTP_400_BAD_REQUEST
        )