from rest_framework import serializers
from .models import Product, BestSelling, Notification, Category, ProductColor, HeroImage


class CategoryChildSerializer(serializers.ModelSerializer):
    """Serializer for child categories (no nesting)"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'order', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model with nested children"""
    children = CategoryChildSerializer(many=True, read_only=True, source='get_all_children')
    parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent_id', 'parent_name', 'order', 'is_active', 'children']


class CategoryTreeSerializer(serializers.ModelSerializer):
    """Serializer for full category tree (parent categories with children)"""
    children = CategoryChildSerializer(many=True, read_only=True, source='get_all_children')
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'order', 'is_active', 'children']


class ProductCategorySerializer(serializers.ModelSerializer):
    """Minimal category serializer for product responses"""
    parent_id = serializers.IntegerField(source='parent.id', read_only=True, allow_null=True)
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    parent_slug = serializers.CharField(source='parent.slug', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent_id', 'parent_name', 'parent_slug']


class ProductColorSerializer(serializers.ModelSerializer):
    """Serializer for ProductColor model"""
    
    class Meta:
        model = ProductColor
        fields = ['id', 'name', 'image', 'order', 'is_active']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model"""
    current_price = serializers.ReadOnlyField()
    has_offer = serializers.ReadOnlyField()
    category = ProductCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True
    )
    # For backward compatibility - returns category slug
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    # Include product colors (only active ones)
    colors = serializers.SerializerMethodField()
    
    def get_colors(self, obj):
        active_colors = obj.colors.filter(is_active=True)
        return ProductColorSerializer(active_colors, many=True, context=self.context).data
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_id', 'category_slug',
            'regular_price', 'offer_price', 'current_price', 'has_offer', 
            'image', 'image2', 'image3', 'image4', 'stock', 'is_active', 
            'colors', 'created_at', 'updated_at'
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


class HeroImageSerializer(serializers.ModelSerializer):
    """Serializer for HeroImage model"""
    
    class Meta:
        model = HeroImage
        fields = ['id', 'image', 'title', 'subtitle', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

