from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import F
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    SimpleOrderSerializer, OrderSerializer, CartSerializer,
    CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer,
    CartCheckoutSerializer
)
from .steadfast_service import SteadfastService
from products.models import Product
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    """API view for creating a new order"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SimpleOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get the product
        try:
            product = Product.objects.get(id=data['product_id'], is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or inactive'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get quantity from request (default to 1)
        quantity = data.get('quantity', 1)
        
        # Check if product is in stock
        if product.stock <= 0:
            return Response(
                {'error': 'Product is out of stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if requested quantity is available
        if quantity > product.stock:
            return Response(
                {'error': f'Only {product.stock} items available in stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Calculate total amount (using current price * quantity)
        total_amount = product.current_price * quantity
        
        # Create the order and reduce stock atomically
        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                session_key=session_key,
                total_amount=total_amount,
                status='pending',
                shipping_address=data['address'],
                shipping_state=data.get('district', ''),  # Store district in shipping_state field
                customer_name=data['customer_name'],
                customer_phone=data['phone_number'],
            )
            
            # Create order item
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.current_price,
                product_size=data.get('product_size', '')
            )
            
            # Reduce product stock atomically
            Product.objects.filter(id=product.id).update(stock=F('stock') - quantity)
        
        # Create order in Steadfast
        steadfast_service = SteadfastService()
        
        # Prepare item description from order items
        item_description = f"{quantity}x {product.name}"
        if data.get('product_size'):
            item_description += f" (Size: {data.get('product_size')})"
        
        # Create invoice ID from order ID
        invoice = f"ORD-{order.id}"
        
        steadfast_response = steadfast_service.create_order(
            invoice=invoice,
            recipient_name=data['customer_name'],
            recipient_phone=data['phone_number'],
            recipient_address=data['address'],
            cod_amount=float(total_amount),
            recipient_email=order.customer_email if order.customer_email else None,
            note=order.notes if order.notes else None,
            item_description=item_description,
            total_lot=quantity,
            delivery_type=0  # 0 for home delivery
        )
        
        # Update order with Steadfast tracking information if successful
        if steadfast_response.get('status') == 200 and steadfast_response.get('consignment'):
            consignment = steadfast_response['consignment']
            order.steadfast_consignment_id = consignment.get('consignment_id')
            order.steadfast_tracking_code = consignment.get('tracking_code', '')
            order.steadfast_status = consignment.get('status', '')
            order.save()
            logger.info(f"Order {order.id} successfully created in Steadfast with consignment ID {order.steadfast_consignment_id}")
        else:
            logger.warning(f"Failed to create order {order.id} in Steadfast: {steadfast_response.get('message', 'Unknown error')}")
        
        # Return the created order
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class CartView(APIView):
    """API view for getting and managing cart"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get current user's cart"""
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        cart, created = Cart.objects.get_or_create(session_key=session_key)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        """Clear entire cart"""
        session_key = request.session.session_key
        if not session_key:
            return Response({'message': 'No cart to clear'}, status=status.HTTP_200_OK)

        try:
            cart = Cart.objects.get(session_key=session_key)
            cart.items.all().delete()
            cart.delete()
            return Response({'message': 'Cart cleared'}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'message': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)


class AddToCartView(APIView):
    """API view for adding items to cart"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        product_id = data['product_id']
        quantity = data.get('quantity', 1)
        
        # Get the product
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found or inactive'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if product is in stock
        if product.stock <= 0:
            return Response(
                {'error': 'Product is out of stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        
        # Check if item already exists in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Item exists, update quantity
            new_quantity = cart_item.quantity + quantity
            # Check stock availability
            if new_quantity > product.stock:
                return Response(
                    {'error': f'Only {product.stock} items available in stock. You already have {cart_item.quantity} in cart.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            # Check if initial quantity exceeds stock
            if cart_item.quantity > product.stock:
                cart_item.delete()
                return Response(
                    {'error': f'Only {product.stock} items available in stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Return updated cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    """API view for updating cart item quantity"""
    permission_classes = [AllowAny]

    def put(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = serializer.validated_data['quantity']
        
        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            return Response(
                {'error': 'No active session'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check stock availability
        if quantity > cart_item.product.stock:
            return Response(
                {'error': f'Only {cart_item.product.stock} items available in stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        cart_item.quantity = quantity
        cart_item.save()
        
        # Return updated cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


class RemoveCartItemView(APIView):
    """API view for removing items from cart"""
    permission_classes = [AllowAny]

    def delete(self, request, item_id):
        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            return Response(
                {'error': 'No active session'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cart = Cart.objects.get(session_key=session_key)
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Cart item not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Return updated cart
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)


class CheckoutFromCartView(APIView):
    """API view for creating an order from cart items"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CartCheckoutSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            return Response(
                {'error': 'No active session'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get cart
        try:
            cart = Cart.objects.get(session_key=session_key)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if cart has items
        cart_items = cart.items.all()
        if not cart_items.exists():
            return Response(
                {'error': 'Cart is empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate all items are in stock
        for item in cart_items:
            if item.quantity > item.product.stock:
                return Response(
                    {'error': f'Product "{item.product.name}" only has {item.product.stock} items in stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Calculate total amount
        total_amount = cart.get_total()
        
        # Create the order, order items, and reduce stock atomically
        product_size = data.get('product_size', '')
        item_descriptions = []
        total_lot = 0
        
        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                session_key=session_key,
                total_amount=total_amount,
                status='pending',
                shipping_address=data['address'],
                shipping_state=data.get('district', ''),
                customer_name=data['customer_name'],
                customer_phone=data['phone_number'],
            )
            
            # Create order items from cart items and reduce stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.current_price,
                    product_size=product_size
                )
                # Reduce product stock atomically
                Product.objects.filter(id=cart_item.product.id).update(stock=F('stock') - cart_item.quantity)
                # Build item description
                item_desc = f"{cart_item.quantity}x {cart_item.product.name}"
                if product_size:
                    item_desc += f" (Size: {product_size})"
                item_descriptions.append(item_desc)
                total_lot += cart_item.quantity
        
        # Create order in Steadfast
        steadfast_service = SteadfastService()
        
        # Combine all item descriptions
        item_description = "; ".join(item_descriptions)
        
        # Create invoice ID from order ID
        invoice = f"ORD-{order.id}"
        
        steadfast_response = steadfast_service.create_order(
            invoice=invoice,
            recipient_name=data['customer_name'],
            recipient_phone=data['phone_number'],
            recipient_address=data['address'],
            cod_amount=float(total_amount),
            recipient_email=order.customer_email if order.customer_email else None,
            note=order.notes if order.notes else None,
            item_description=item_description,
            total_lot=total_lot,
            delivery_type=0  # 0 for home delivery
        )
        
        # Update order with Steadfast tracking information if successful
        if steadfast_response.get('status') == 200 and steadfast_response.get('consignment'):
            consignment = steadfast_response['consignment']
            order.steadfast_consignment_id = consignment.get('consignment_id')
            order.steadfast_tracking_code = consignment.get('tracking_code', '')
            order.steadfast_status = consignment.get('status', '')
            order.save()
            logger.info(f"Order {order.id} successfully created in Steadfast with consignment ID {order.steadfast_consignment_id}")
        else:
            logger.warning(f"Failed to create order {order.id} in Steadfast: {steadfast_response.get('message', 'Unknown error')}")
        
        # Clear the cart after successful order
        cart.items.all().delete()
        cart.delete()
        
        # Return the created order
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)
