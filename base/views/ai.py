from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from inference_sdk import InferenceHTTPClient
from rest_framework import status
import io , os

from ..ai_stuff.smart_nlp import doTheJob

# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def dog (request):
    message = request.data['message']
    result_text = doTheJob(message)
    return Response(result_text, status= status.HTTP_200_OK)
   
   