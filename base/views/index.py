from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes

@api_view(['GET'])
def index (request):
    return Response({"server running well"})
