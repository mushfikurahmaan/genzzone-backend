from .models import Cart, CartItem
from products.models import Product


def get_or_create_cart(session_key):
    """Get or create a cart for a given session key"""
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def get_cart(session_key):
    """Get cart for a given session key, return None if doesn't exist"""
    try:
        return Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        return None


def add_to_cart(cart, product_id, quantity=1):
    """Add a product to cart or update quantity if already exists"""
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        raise ValueError("Product not found or inactive")

    if product.stock < quantity:
        raise ValueError(f"Insufficient stock. Available: {product.stock}")

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            raise ValueError(f"Insufficient stock. Available: {product.stock}, Requested: {new_quantity}")
        cart_item.quantity = new_quantity
        cart_item.save()

    return cart_item


def update_cart_item(cart, cart_item_id, quantity):
    """Update quantity of a cart item"""
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
    except CartItem.DoesNotExist:
        raise ValueError("Cart item not found")

    if quantity > cart_item.product.stock:
        raise ValueError(f"Insufficient stock. Available: {cart_item.product.stock}")

    cart_item.quantity = quantity
    cart_item.save()
    return cart_item


def remove_from_cart(cart, cart_item_id):
    """Remove an item from cart"""
    try:
        cart_item = CartItem.objects.get(id=cart_item_id, cart=cart)
        cart_item.delete()
        return True
    except CartItem.DoesNotExist:
        return False


def clear_cart(cart):
    """Clear all items from cart"""
    cart.items.all().delete()

