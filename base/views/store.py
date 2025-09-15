from rest_framework.response import Response
from ..models import Store, Product
from django.contrib.auth import get_user_model
from django.conf import settings
User = get_user_model()
from rest_framework import generics, permissions, status, serializers
from ..serializers import StoreReadSerializer, StoreWriteSerializer

# Create store
class StoreCreateView(generics.CreateAPIView):
    serializer_class = StoreWriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if Store.objects.filter(user=user).exists():
            raise serializers.ValidationError({"message": "A store already exists for this user."})
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        store = Store.objects.get(id=response.data['id'])
        return Response(StoreReadSerializer(store).data, status=status.HTTP_201_CREATED)


# Retrieve store
class StoreDetailView(generics.RetrieveAPIView):
    queryset = Store.objects.select_related('user')
    serializer_class = StoreReadSerializer
    permission_classes = []
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        store = self.get_object()
        data = StoreReadSerializer(store).data

        # Remove store fields from each product to avoid duplication
        for product in data['products']:
            product.pop('store_id', None)
            product.pop('store_name', None)
            product.pop('logo', None)

        return Response(data)



# Delete store
class StoreDeleteView(generics.DestroyAPIView):
    queryset = Store.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            self.permission_denied(self.request, message="user does not have this store")
        Product.objects.filter(user=self.request.user).delete()
        instance.delete()


# Update store logo
class StoreUpdateLogoView(generics.UpdateAPIView):
    queryset = Store.objects.all()
    serializer_class = StoreReadSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        store = self.get_object()
        if store.user != request.user:
            return Response({"message": "user does not have this store"}, status=status.HTTP_401_UNAUTHORIZED)

        photo = request.FILES.get('logo')
        if not photo:
            return Response({"message": "photo is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Validate image
            image = Image.open(photo)
            image.verify()

            # Delete old logo
            if store.logo and os.path.isfile(store.logo.path):
                os.remove(store.logo.path)

            store.logo = photo
            store.save()

            return Response(StoreReadSerializer(store).data, status=status.HTTP_200_OK)

        except (IOError, SyntaxError):
            return Response({"message": "Uploaded file is not a valid image"}, status=status.HTTP_400_BAD_REQUEST)
