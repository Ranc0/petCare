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
from ..models import Doctor, DoctorPost, PendingUser
from ..serializers import DoctorPostSerializer
from PIL import Image
import os
from django.contrib.auth import get_user_model
from ..utils import *

User = get_user_model()

def generate_and_send_otp(user):
    otp = str(random.randint(100000, 999999))
    cache_key = f'otp_{user.id}'
    cache.set(cache_key, otp, timeout=300)

    if settings.SEND_OTP_EMAIL:
        send_mail(
            'Your OTP Code',
            f'Your verification code is: {otp}',
            'PertCareApp',
            [user.email],
            fail_silently=False,
        )
        #send_otp_email(email, otp)
    return otp

def handle_otp_verification(user_id, submitted_otp, request_status):
    cache_key = f'otp_{user_id}'
    cached_otp = cache.get(cache_key)

    if not cached_otp:
        return False, "OTP expired or doesn't exist", None

    if cached_otp != submitted_otp:
        return False, "Invalid OTP", None

    cache.delete(cache_key)
    print(request_status)
    if request_status == 'sign_up':
        pending_user = PendingUser.objects.get(id = user_id)
        user = User.objects.create(username=pending_user.username, email=pending_user.email,first_name = pending_user.first_name, last_name = pending_user.last_name,country = pending_user.country)
        user.set_password(pending_user.password)
        user.save()
        pending_user.delete()
    else:
        user = User.objects.get(id = user_id)
    
    return True, "OTP verified successfully", user

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
    first_name = request.data.get('first_name',None)
    last_name = request.data.get('last_name',None)
    country = request.data.get('country',None)

    if User.objects.filter(username=username).exists() or PendingUser.objects.filter(username=username).exists() :
        return Response({"message": "Username exists"}, status=status.HTTP_409_CONFLICT)
    if User.objects.filter(email=email).exists() or PendingUser.objects.filter(email=email).exists():
        return Response({"message": "Email exists"}, status=status.HTTP_409_CONFLICT)
    if password != confirm_password:
        return Response({"message": "Passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)

    pending_user = PendingUser.objects.create(username=username,email=email, first_name = first_name, last_name = last_name, password = password)
    if country:
        pending_user.country = country
        pending_user.save()


    otp_sent = generate_and_send_otp(pending_user)
    return Response({
        "message": "OTP sent to your email",
        "otp": otp_sent,
        "user_id": pending_user.id
    })

@api_view(['GET'])
def forgot_password(request, id):
    user = get_object_or_404(User, id = id)
    otp_sent = generate_and_send_otp(user)
    return Response({
        "message": "OTP sent to your email",
        "otp": otp_sent,
        "user_id": user.id
    })

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
    user = get_object_or_404(User, id = id)
    response = {"username":user.username, 
                "email":user.email, 
                "first_name":"Dr."+user.first_name, 
                "last_name":user.last_name,
                "user_photo": user.user_photo.url if user.user_photo else None}
    #photo = UserPhoto(user = user)
    #response.update({"user_photo":photo.user_photo.url if photo.user_photo else None})
    
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
    photo = request.FILES.get("user_photo")
    if not photo:
        return Response({"message": "user photo is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Validate the uploaded file as an image
        image = Image.open(photo)
        image.verify()  # Verify the image integrity

        # Delete the old photo if it exists
        if user.user_photo and os.path.isfile(user.user_photo.path):
            os.remove(user.user_photo.path)

        # Update the photo field
        user.user_photo = photo
        user.save()

        # Serialize the updated pet object
        response= {"user_photo":user.user_photo.url if user.user_photo else None}
        return Response(response, status=status.HTTP_200_OK)

    except (IOError, SyntaxError):
        return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)