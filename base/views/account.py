#from rest_framework.decorators import api_view
#from rest_framework.response import Response
#from rest_framework import status
#from django.contrib.auth import authenticate
#from rest_framework_simplejwt.tokens import RefreshToken
#from django.contrib.auth.models import User
#from validate_email import validate_email

#@api_view(['POST'])
#def sign_in(request):

    # sign in using email can be added 
#    username = request.data['username']
#    password = request.data['password']
#    user = authenticate(username=username, password=password)
#    if user:
#        refresh = RefreshToken.for_user(user)
#        return Response({
#        'refresh': str(refresh),
#        'access': str(refresh.access_token),
#    })
#    else :
#        return Response({"message":"couldn't sign in"} , status = status.HTTP_401_UNAUTHORIZED)
    
#@api_view(['POST'])
#def sign_up(request):
    #you do it 
#    username = request.data['username']
#    password = request.data['password']
#    confirm_password = request.data['confirm_password']
#    if User.objects.filter(username__iexact = username).exists():
#        return Response({"message":"username already exists"} , status = status.HTTP_409_CONFLICT)
#    if password != confirm_password:
#        return Response({"message":"passwords do not match"} , status = status.HTTP_409_CONFLICT)
#    user = User.objects.create(username = username)
#    user.set_password(password)
#    user.save()
#    refresh = RefreshToken.for_user(user)
#    return Response({
#        'refresh': str(refresh),
#        'access': str(refresh.access_token),
#    })
import random
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from ..models import Doctor, DoctorPost
from ..serializers import DoctorPostSerializer
from PIL import Image
import os
from django.contrib.auth import get_user_model

User = get_user_model()

def generate_and_send_otp(user):
    otp = str(random.randint(100000, 999999))
    cache_key = f'otp_{user.id}'
    cache.set(cache_key, otp, timeout=5000000)

    if settings.SEND_OTP_EMAIL:
        send_mail(
            'Your OTP Code',
            f'Your verification code is: {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    return otp

def handle_otp_verification(user_id, submitted_otp):
    cache_key = f'otp_{user_id}'
    cached_otp = cache.get(cache_key)

    if not cached_otp:
        return False, "OTP expired or doesn't exist"

    if cached_otp != submitted_otp:
        return False, "Invalid OTP"

    cache.delete(cache_key)
    return True, "OTP verified successfully"

@api_view(['POST'])
def verify_otp(request):
    user_id = request.data.get('user_id')
    otp = request.data.get('otp')

    if not user_id or not otp:
        return Response({"error": "user_id and otp are required"},
                        status=status.HTTP_400_BAD_REQUEST)

    is_valid, message = handle_otp_verification(user_id, otp)
    if not is_valid:
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.is_active = True
    user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['POST'])
def sign_in(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if not user:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    user.is_active = True
    user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['POST'])
def sign_up(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    confirm_password = request.data.get('confirm_password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')

    if User.objects.filter(username=username).exists():
        return Response({"message": "Username exists"}, status=status.HTTP_409_CONFLICT)
    if password != confirm_password:
        return Response({"message": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(username=username, email=email, first_name = first_name, last_name = last_name, is_active=False)
    user.set_password(password)
    user.save()
    user_photo = UserPhoto.objects.create(user_photo = None, user = user)

    otp_sent = generate_and_send_otp(user)
    return Response({
        "message": "OTP sent to your email",
        "otp": otp_sent,
        "user_id": user.id
    })

@api_view(['GET'])
def get_account(request, id):
    user = get_object_or_404(User, id = id)
    response = {"username":user.username, "email":user.email, "first_name":"Dr."+user.first_name, "last_name":user.last_name}
    photo = UserPhoto(user = user)
    response.update({"user_photo":photo.user_photo.url if photo.user_photo else None})
    
    if Doctor.objects.filter(user = user):
        doctor = Doctor.objects.get(user = user)
        response.update({"experience":doctor.experience})
        holder = []
        posts = DoctorPost.objects.filter(user = user)
        for post in posts:
            post = DoctorPostSerializer(post).data
            holder.append(post)
        response.update({"posts":holder})
    return Response(response, status= status.HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(['PUT'])
def update_user_photo(request, id):
    user = User.objects.filter(id = id)
    if user:
        user = user[0]
    else:
        return Response({"message":"user not found"}, status= status.HTTP_404_NOT_FOUND)
    photo = request.FILES.get('user_photo')
    if not photo:
        return Response({"message": "user photo is required"}, status=status.HTTP_400_BAD_REQUEST)
    user_photo = UserPhoto.objects.get(user = user)

    try:
        # Validate the uploaded file as an image
        image = Image.open(photo)
        image.verify()  # Verify the image integrity

        # Delete the old photo if it exists
        if user_photo.user_photo and os.path.isfile(user_photo.user_photo.path):
            os.remove(user_photo.user_photo.path)

        # Update the photo field
        user_photo.user_photo = photo
        user_photo.save()

        # Serialize the updated pet object
        response= {"user_photo":user_photo.user_photo.url if user_photo.user_photo else None}
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)