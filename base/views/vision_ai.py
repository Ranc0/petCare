from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from inference_sdk import InferenceHTTPClient
from rest_framework import status
from PIL import Image
import io , os
from dotenv import load_dotenv


@permission_classes([IsAuthenticated])
@api_view(['POST'])
def dog_vision (request):
    load_dotenv()
    user = request.user
    key = os.getenv("API_KEY")
    CLIENT = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=key
    )
    your_image = request.FILES.get('photo')
    image = Image.open(io.BytesIO(your_image.read()))
    data = CLIENT.infer(image, model_id="dog-skin-diseases/1")
    results = [(pred['class'], pred['confidence']) for pred in data['predictions']]
    # print(data)
    result = [
        {"diagnosis": cls, "confidence": round(conf * 100, 2)}
        for cls, conf in results
    ]
    return Response(result, status= status.HTTP_200_OK)

# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def cat_vision (request):
    load_dotenv()
    user = request.user
    key = os.getenv("API_KEY")
    CLIENT = InferenceHTTPClient(
        api_url="https://serverless.roboflow.com",
        api_key=key
    )
    your_image = request.FILES.get('photo')
    image = Image.open(io.BytesIO(your_image.read()))
    data = CLIENT.infer(image, model_id="cat-skin-disease/3")
    results = [(pred['class'], pred['confidence']) for pred in data['predictions']]
    # print(data)
    result = [
        {"diagnosis": cls, "confidence": round(conf * 100, 2)}
        for cls, conf in results
    ]

    return Response(result, status= status.HTTP_200_OK)