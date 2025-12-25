from rest_framework import serializers
from .models import Product, BestSelling, Notification


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    current_price = serializers.ReadOnlyField()
    has_offer = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'regular_price', 'offer_price', 
            'current_price', 'has_offer', 'image', 'stock', 'is_active', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'current_price', 'has_offer']


class BestSellingSerializer(serializers.ModelSerializer):
    """Serializer for BestSelling model"""
    product = ProductSerializer(read_only=True)
    
    class Meta:
        model = BestSelling
        fields = ['id', 'product', 'order', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

