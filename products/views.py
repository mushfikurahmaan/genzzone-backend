from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, BestSelling, Notification
from .serializers import ProductSerializer, BestSellingSerializer, NotificationSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        # Optional: Add search/filter functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        # Category filtering
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        return queryset


class BestSellingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing best selling products"""
    queryset = BestSelling.objects.filter(is_active=True, product__is_active=True)
    serializer_class = BestSellingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return BestSelling.objects.filter(
            is_active=True,
            product__is_active=True
        ).select_related('product')


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications"""
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get the currently active notification"""
        notification = Notification.objects.filter(is_active=True).first()
        if notification:
            serializer = self.get_serializer(notification)
            return Response(serializer.data)
        return Response({'message': '', 'is_active': False})
