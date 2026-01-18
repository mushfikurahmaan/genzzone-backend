from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, BestSelling, Notification, Category
from .serializers import (
    ProductSerializer, BestSellingSerializer, NotificationSerializer,
    CategorySerializer, CategoryTreeSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing categories"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        return Category.objects.filter(is_active=True).select_related('parent')

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get category tree structure (only parent categories with their children)"""
        parent_categories = Category.objects.filter(
            is_active=True,
            parent__isnull=True
        ).prefetch_related('children').order_by('order', 'name')
        serializer = CategoryTreeSerializer(parent_categories, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing products"""
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category', 'category__parent')
        # Optional: Add search/filter functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Category filtering by slug
        category = self.request.query_params.get('category', None)
        if category:
            # Filter by category slug - includes products in this category
            # or in child categories if this is a parent category
            try:
                cat = Category.objects.get(slug=category, is_active=True)
                if cat.parent is None:
                    # Parent category - get products from this category and all children
                    child_ids = cat.children.filter(is_active=True).values_list('id', flat=True)
                    queryset = queryset.filter(category_id__in=[cat.id] + list(child_ids))
                else:
                    # Child category - get products only from this category
                    queryset = queryset.filter(category=cat)
            except Category.DoesNotExist:
                queryset = queryset.none()
        
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
