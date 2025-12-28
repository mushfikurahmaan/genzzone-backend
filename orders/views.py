from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.db.models import F
from django.db import transaction
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    SimpleOrderSerializer, OrderSerializer, CartSerializer,
    CartItemSerializer, AddToCartSerializer, UpdateCartItemSerializer
)
from .steadfast_service import SteadfastService
from products.models import Product
import logging

logger = logging.getLogger(__name__)


class CreateOrderView(APIView):
    """API view for creating a new order with multiple products"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SimpleOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        products_data = data['products']
        
        # Validate products array is not empty
        if not products_data:
            return Response(
                {'error': 'At least one product is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate all products exist and are in stock
        products_to_order = []
        for product_data in products_data:
            product_id = product_data['product_id']
            quantity = product_data['quantity']
            
            try:
                product = Product.objects.get(id=product_id, is_active=True)
            except Product.DoesNotExist:
                return Response(
                    {'error': f'Product with ID {product_id} not found or inactive'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check if product is in stock
            if product.stock <= 0:
                return Response(
                    {'error': f'Product "{product.name}" is out of stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if requested quantity is available
            if quantity > product.stock:
                return Response(
                    {'error': f'Product "{product.name}" only has {product.stock} items available in stock'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use unit_price from request if provided, otherwise use product's current_price
            unit_price = product_data.get('unit_price')
            if unit_price is None:
                unit_price = product.current_price
            
            products_to_order.append({
                'product': product,
                'quantity': quantity,
                'price': unit_price,
                'product_size': product_data.get('product_size', '')
            })
        
        # Get or create session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        # Use total_price from frontend (includes delivery charge)
        total_amount = data['total_price']
        
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
            
            # Create order items for each product
            for product_info in products_to_order:
                OrderItem.objects.create(
                    order=order,
                    product=product_info['product'],
                    quantity=product_info['quantity'],
                    price=product_info['price'],
                    product_size=product_info['product_size']
                )
                
                # Reduce product stock atomically
                Product.objects.filter(id=product_info['product'].id).update(
                    stock=F('stock') - product_info['quantity']
                )
        
        # Order is saved and will be sent to Steadfast later via admin panel
        logger.info(f"Order {order.id} created successfully with {len(products_to_order)} product(s). Waiting for admin approval to send to Steadfast.")
        
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


class SendOrderToSteadfastView(APIView):
    """Admin API view for sending an order to Steadfast"""
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, order_id):
        """Send an order to Steadfast"""
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order is already sent to Steadfast
        if order.steadfast_consignment_id:
            return Response(
                {'error': 'Order has already been sent to Steadfast', 
                 'consignment_id': order.steadfast_consignment_id,
                 'tracking_code': order.steadfast_tracking_code},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare item description from order items
        item_descriptions = []
        total_lot = 0
        
        for order_item in order.items.all():
            item_desc = f"{order_item.quantity}x {order_item.product.name}"
            if order_item.product_size:
                item_desc += f" (Size: {order_item.product_size})"
            item_descriptions.append(item_desc)
            total_lot += order_item.quantity
        
        item_description = "; ".join(item_descriptions)
        
        # Create invoice ID from order ID
        invoice = f"ORD-{order.id}"
        
        # Send order to Steadfast
        steadfast_service = SteadfastService()
        
        steadfast_response = steadfast_service.create_order(
            invoice=invoice,
            recipient_name=order.customer_name,
            recipient_phone=order.customer_phone,
            recipient_address=order.shipping_address,
            cod_amount=float(order.total_amount),
            recipient_email=order.customer_email if order.customer_email else None,
            note=None,
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
            order.status = 'sent'  # Update order status to sent
            order.save()
            logger.info(f"Order {order.id} successfully sent to Steadfast with consignment ID {order.steadfast_consignment_id}")
            
            return Response({
                'message': 'Order successfully sent to Steadfast',
                'order_id': order.id,
                'consignment_id': order.steadfast_consignment_id,
                'tracking_code': order.steadfast_tracking_code,
                'status': order.steadfast_status
            }, status=status.HTTP_200_OK)
        else:
            error_message = steadfast_response.get('message', 'Unknown error')
            logger.warning(f"Failed to send order {order.id} to Steadfast: {error_message}")
            
            return Response({
                'error': 'Failed to send order to Steadfast',
                'message': error_message
            }, status=status.HTTP_400_BAD_REQUEST)
