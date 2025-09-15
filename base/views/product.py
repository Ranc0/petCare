from rest_framework.response import Response
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Pet  , Product, Store
from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework import status
from django.db.models import Q
from PIL import Image
import os
from django.shortcuts import get_object_or_404
from django.conf import settings

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from ..serializers import ProductReadSerializer, ProductWriteSerializer

# Create product
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductWriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        store = get_object_or_404(Store, user=user)
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        product = Product.objects.select_related('user').get(id=response.data['id'])
        return Response(ProductReadSerializer(product).data, status=status.HTTP_201_CREATED)


# Delete product
class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            self.permission_denied(self.request, message="user does not have this product")
        instance.delete()


# List all products (public)
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.select_related('user', 'user__store').all()
    serializer_class = ProductReadSerializer
    permission_classes = []


# Retrieve single product (public)
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('user', 'user__store').all()
    serializer_class = ProductReadSerializer
    permission_classes = []
    lookup_field = 'id'


from rest_framework.views import APIView


class ProductFilterView(APIView):
    permission_classes = []  # Public

    def post(self, request):
        filter_params = {
            'category': request.data.get('category'),
        }
        price = request.data.get('price')
        country = request.data.get('country')

        if price:
            filter_params['price__lte'] = price
        if country:
            filter_params['user__country'] = country

        filter_params = {k: v for k, v in filter_params.items() if v is not None}

        products = Product.objects.select_related('user', 'user__store').filter(**filter_params)
        serializer = ProductReadSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from django.db.models import Q

class ProductSearchView(APIView):
    permission_classes = []  # Public

    def post(self, request):
        text = request.data.get('text')
        product_filter = Q()
        if text:
            product_filter = (
                Q(name__icontains=text) |
                Q(details__icontains=text) |
                Q(category__icontains=text)
            )

        products = Product.objects.select_related('user', 'user__store').filter(product_filter)
        serializer = ProductReadSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProductPhotoView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        product = self.get_object()
        if product.user != request.user:
            return Response({"message": "user does not have this product"}, status=status.HTTP_401_UNAUTHORIZED)

        photo = request.FILES.get('photo')
        if not photo:
            return Response({"message": "photo is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate image
            image = Image.open(photo)
            image.verify()

            # Delete old photo if exists
            if product.photo and os.path.isfile(product.photo.path):
                os.remove(product.photo.path)

            product.photo = photo
            product.save()

            return Response(ProductReadSerializer(product).data, status=status.HTTP_200_OK)

        except (IOError, SyntaxError):
            return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)
