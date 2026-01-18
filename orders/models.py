from django.db import models
from django.core.validators import MinValueValidator
from products.models import Product


class Cart(models.Model):
    """Cart model linked to session"""
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Cart {self.session_key[:8]}"

    def get_total(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_subtotal() for item in self.items.all())

    def get_item_count(self):
        """Get total quantity of items in cart"""
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Items in a cart"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.product.current_price * self.quantity


class Order(models.Model):
    """Order model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    session_key = models.CharField(max_length=40, db_index=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100, blank=True, default='')
    shipping_state = models.CharField(max_length=100, blank=True, default='')
    shipping_zip = models.CharField(max_length=20, blank=True, default='')
    shipping_country = models.CharField(max_length=100, blank=True, default='Bangladesh')
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField(blank=True, default='')
    customer_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    # Steadfast integration fields
    steadfast_consignment_id = models.IntegerField(null=True, blank=True, help_text='Steadfast consignment ID')
    steadfast_tracking_code = models.CharField(max_length=50, blank=True, help_text='Steadfast tracking code')
    steadfast_status = models.CharField(max_length=50, blank=True, help_text='Current Steadfast delivery status')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    """Items in an order"""
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Store price at time of order
    product_size = models.CharField(max_length=50, blank=True, help_text='Product size selected by customer')
    product_image = models.URLField(max_length=500, blank=True, help_text='Product image URL at time of order')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_subtotal(self):
        """Calculate subtotal for this order item"""
        return self.price * self.quantity
