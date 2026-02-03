from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify
from decimal import Decimal


class Category(models.Model):
    """Hierarchical category model for products"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_parent(self):
        """Returns True if this category has children"""
        return self.children.exists()

    def get_all_children(self):
        """Returns all child categories"""
        return self.children.filter(is_active=True).order_by('order', 'name')


class Product(models.Model):
    """Product model for e-commerce items"""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
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
    image2 = models.ImageField(upload_to='products/', blank=True, null=True, help_text='Second product image')
    image3 = models.ImageField(upload_to='products/', blank=True, null=True, help_text='Third product image')
    image4 = models.ImageField(upload_to='products/', blank=True, null=True, help_text='Fourth product image')
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


class ProductColor(models.Model):
    """Model for product color options with images"""
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='colors'
    )
    name = models.CharField(
        max_length=100,
        help_text='Color name (e.g., Red, Blue, Navy Blue)'
    )
    image = models.ImageField(
        upload_to='products/colors/',
        help_text='Image showing the product in this color'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Display order (lower numbers appear first)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Product Color'
        verbose_name_plural = 'Product Colors'

    def __str__(self):
        return f"{self.product.name} - {self.name}"


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


class HeroImage(models.Model):
    """Model for the website hero section image (and optional overlay text)."""
    image = models.ImageField(
        upload_to='hero/',
        help_text='Hero banner image displayed on the homepage'
    )
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text='Optional headline text overlay on the hero'
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        help_text='Optional subtext overlay on the hero'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Only the active hero image is shown on the site'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Hero Image'
        verbose_name_plural = 'Hero Images'

    def __str__(self):
        return self.title or f'Hero Image #{self.pk}'

    def save(self, *args, **kwargs):
        # Ensure only one active hero image at a time
        if self.is_active:
            HeroImage.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
