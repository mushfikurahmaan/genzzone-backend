from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, BestSellingViewSet, NotificationViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'best-selling', BestSellingViewSet, basename='best-selling')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('api/', include(router.urls)),
]

