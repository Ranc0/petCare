from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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
    pass 

#email validators can be added as well 