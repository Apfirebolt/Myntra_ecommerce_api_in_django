import qrcode
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from . serializers import ListCustomUserSerializer, CustomUserSerializer, CustomTokenObtainPairSerializer, ListItemsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from rest_framework.response import Response
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_simplejwt.views import TokenObtainPairView
from api.models import CustomUser, Item
from django.db import connection
from django.conf import settings
from . pagination import CustomPagination


class CreateCustomUserApiView(CreateAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

class CustomTokenObtainPairView(TokenObtainPairView):
    # Replace the serializer with your custom
    serializer_class = CustomTokenObtainPairSerializer


class ListCustomUsersApiView(ListAPIView):
    serializer_class = ListCustomUserSerializer
    queryset = CustomUser.objects.all()


class ListItemApiView(ListAPIView):
    serializer_class = ListItemsSerializer
    pagination_class = CustomPagination
    # limit the number of requests per user to 5 in 1 minute
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['title', 'brand']
    ordering_fields = ['price']
    search_fields = ['title', 'brand']
    # permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        cache_key = self.generate_cache_key(request)
        cached_data = cache.get(cache_key)

        if cached_data:
            return self.handle_cached_data(cached_data)

        response = super().get(request, *args, **kwargs)

        if response.status_code == 200:
            self.cache_response(cache_key, response.data)

        return response
    
    def get_queryset(self):
        # Filter by items whose price is greater than 100
        return Item.objects.all()
    
    def generate_cache_key(self, request):
        """Generates a unique cache key based on the request."""
        query_params = request.query_params.copy()
        query_params_str = str(sorted(query_params.items()))
        return f"list_items_api:{query_params_str}"

    def handle_cached_data(self, cached_data):
        """Handles returning cached data as a response."""
        return Response(cached_data)

    def cache_response(self, cache_key, data):
        """Caches the response data."""
        cache.set(cache_key, data, settings.CACHE_TTL if hasattr(settings, 'CACHE_TTL') else 60)  # Default TTL 60 seconds



class DetailItemApiView(RetrieveAPIView):
    serializer_class = ListItemsSerializer
    queryset = Item.objects.all()
    lookup_field = 'id'


class QRCodeApiView(APIView):

    def get(self, request, *args, **kwargs):
        data = "https://www.apgiiit.com"  # Replace with your data

        qr = qrcode.make(data, version=1, box_size=10)  # Optional parameters
        
        # save qg code image in a new media folder
        qr.save('media/qrcode.png')
        return Response({'message': 'This is a QR code API view'})
    




