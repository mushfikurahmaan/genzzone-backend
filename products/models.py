from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Product(models.Model):
    """Product model for e-commerce items"""
    
    CATEGORY_CHOICES = [
        ('men', 'Men'),
        ('womens', 'Womens'),
        ('combo', 'Combo'),
        ('shirt-combo', 'Shirt Combo'),
        ('panjabi-combo', 'Panjabi Combo'),
        ('shirts', 'Shirts'),
        ('panjabi', 'Panjabi'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='men',
        help_text='Product category'
    )
    regular_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Regular price of the product',
        default=Decimal('0.01')
    )
    offer_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        blank=True,
        null=True,
        help_text='Offer price (optional). If not set, regular price will be shown.'
    )
    # Keep price field for backward compatibility - returns offer_price if available, else regular_price
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        blank=True,
        null=True,
        help_text='Deprecated: Use regular_price and offer_price instead'
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
    
    @property
    def current_price(self):
        """Returns offer_price if available, otherwise regular_price"""
        return self.offer_price if self.offer_price else self.regular_price
    
    @property
    def has_offer(self):
        """Returns True if product has an offer price"""
        return self.offer_price is not None and self.offer_price < self.regular_price


class BestSelling(models.Model):
    """Model to mark products as best selling"""
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='best_selling'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Order in which products appear (lower numbers appear first)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = 'Best Selling Product'
        verbose_name_plural = 'Best Selling Products'

    def __str__(self):
        return f"Best Selling: {self.product.name}"


class Notification(models.Model):
    """Model for site-wide notification banner message"""
    message = models.CharField(
        max_length=500,
        help_text='Notification message to display in the navbar banner'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the notification is currently displayed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return self.message[:50] + ('...' if len(self.message) > 50 else '')
    
    def save(self, *args, **kwargs):
        # Ensure only one active notification at a time
        if self.is_active:
            Notification.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
