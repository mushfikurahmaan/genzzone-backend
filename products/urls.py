from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, BestSellingViewSet, NotificationViewSet, CategoryViewSet, HeroImageViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'best-selling', BestSellingViewSet, basename='best-selling')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'hero-image', HeroImageViewSet, basename='hero-image')

urlpatterns = [
    path('api/', include(router.urls)),
]

