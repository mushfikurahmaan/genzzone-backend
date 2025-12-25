from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem with product details"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart with items"""
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'session_key', 'items', 'total', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['session_key', 'created_at', 'updated_at']

    def get_total(self, obj):
        return obj.get_total()

    def get_item_count(self, obj):
        return obj.get_item_count()


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem"""
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'product_size', 'subtotal', 'created_at']
        read_only_fields = ['created_at']

    def get_subtotal(self, obj):
        return obj.get_subtotal()


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order with items"""
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'session_key', 'total_amount', 'status', 'shipping_address',
            'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country',
            'customer_name', 'customer_email', 'customer_phone', 'notes',
            'steadfast_consignment_id', 'steadfast_tracking_code', 'steadfast_status',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['session_key', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer for creating an order"""
    shipping_address = serializers.CharField()
    shipping_city = serializers.CharField()
    shipping_state = serializers.CharField()
    shipping_zip = serializers.CharField()
    shipping_country = serializers.CharField()
    customer_name = serializers.CharField()
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class SimpleOrderSerializer(serializers.Serializer):
    """Simplified serializer for creating an order from product page"""
    customer_name = serializers.CharField(max_length=200)
    district = serializers.CharField(max_length=100)
    address = serializers.CharField()  # Full address as text
    phone_number = serializers.CharField(max_length=20)
    product_id = serializers.IntegerField()
    product_size = serializers.CharField(max_length=50, allow_blank=True)
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartCheckoutSerializer(serializers.Serializer):
    """Serializer for creating an order from cart"""
    customer_name = serializers.CharField(max_length=200)
    district = serializers.CharField(max_length=100)
    address = serializers.CharField()  # Full address as text
    phone_number = serializers.CharField(max_length=20)
    product_size = serializers.CharField(max_length=50, allow_blank=True, required=False)

