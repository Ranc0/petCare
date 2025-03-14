from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from validate_email import validate_email

@api_view(['POST'])
def sign_in(request):

    # sign in using email can be added 
    username = request.data['username']
    password = request.data['password']
    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })
    else :
        return Response({"message":"couldn't sign in"} , status = status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
def sign_up(request):
    #you do it 
    username = request.data['username']
    password = request.data['password']
    confirm_password = request.data['confirm_password']
    if User.objects.filter(username__iexact = username).exists():
        return Response({"message":"username already exists"} , status = status.HTTP_409_CONFLICT)
    if password != confirm_password:
        return Response({"message":"passwords do not match"} , status = status.HTTP_409_CONFLICT)
    user = User.objects.create(username = username, password = password)
    user.save()
    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

#email validators can be added as well 