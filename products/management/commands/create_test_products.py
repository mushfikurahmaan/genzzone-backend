from django.core.management.base import BaseCommand
from products.models import Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Creates 30 test products with different categories'

    def handle(self, *args, **options):
        # Product data with variety
        products_data = [
            # Men's Products (10)
            {'name': 'Classic Black Premium T-Shirt', 'description': 'Comfortable and stylish black t-shirt made from premium cotton. Perfect for everyday wear.', 'category': 'men', 'regular_price': Decimal('899.00'), 'offer_price': Decimal('699.00'), 'stock': 50},
            {'name': 'Navy Blue Casual Tee', 'description': 'Soft navy blue t-shirt with modern fit. Great for casual outings and weekend wear.', 'category': 'men', 'regular_price': Decimal('850.00'), 'offer_price': None, 'stock': 75},
            {'name': 'White Classic Crew Neck', 'description': 'Timeless white crew neck t-shirt. Versatile and essential for any wardrobe.', 'category': 'men', 'regular_price': Decimal('799.00'), 'offer_price': Decimal('599.00'), 'stock': 100},
            {'name': 'Gray Premium Cotton Tee', 'description': 'Premium quality gray t-shirt with excellent breathability and comfort.', 'category': 'men', 'regular_price': Decimal('950.00'), 'offer_price': None, 'stock': 60},
            {'name': 'Olive Green Street Style Tee', 'description': 'Trendy olive green t-shirt perfect for street style enthusiasts.', 'category': 'men', 'regular_price': Decimal('899.00'), 'offer_price': Decimal('749.00'), 'stock': 45},
            {'name': 'Charcoal Slim Fit T-Shirt', 'description': 'Slim fit charcoal t-shirt with modern design. Perfect for a sleek look.', 'category': 'men', 'regular_price': Decimal('999.00'), 'offer_price': None, 'stock': 80},
            {'name': 'Burgundy Premium Tee', 'description': 'Rich burgundy colored t-shirt made from premium materials.', 'category': 'men', 'regular_price': Decimal('879.00'), 'offer_price': Decimal('699.00'), 'stock': 55},
            {'name': 'Beige Comfort Fit T-Shirt', 'description': 'Comfortable beige t-shirt with relaxed fit. Ideal for casual comfort.', 'category': 'men', 'regular_price': Decimal('799.00'), 'offer_price': None, 'stock': 70},
            {'name': 'Royal Blue Classic Tee', 'description': 'Vibrant royal blue t-shirt with classic design. Stand out in style.', 'category': 'men', 'regular_price': Decimal('929.00'), 'offer_price': Decimal('799.00'), 'stock': 65},
            {'name': 'Black Premium V-Neck', 'description': 'Stylish black v-neck t-shirt for a sophisticated casual look.', 'category': 'men', 'regular_price': Decimal('949.00'), 'offer_price': None, 'stock': 40},
            
            # Women's Products (10)
            {'name': 'Pink Floral Print T-Shirt', 'description': 'Beautiful pink t-shirt with floral design. Feminine and elegant.', 'category': 'womens', 'regular_price': Decimal('899.00'), 'offer_price': Decimal('699.00'), 'stock': 60},
            {'name': 'White Oversized Comfort Tee', 'description': 'Comfortable oversized white t-shirt perfect for relaxed style.', 'category': 'womens', 'regular_price': Decimal('849.00'), 'offer_price': None, 'stock': 85},
            {'name': 'Lavender Soft Cotton Tee', 'description': 'Soft lavender colored t-shirt made from premium cotton blend.', 'category': 'womens', 'regular_price': Decimal('929.00'), 'offer_price': Decimal('749.00'), 'stock': 50},
            {'name': 'Coral Summer T-Shirt', 'description': 'Vibrant coral t-shirt perfect for summer days. Light and breathable.', 'category': 'womens', 'regular_price': Decimal('879.00'), 'offer_price': None, 'stock': 70},
            {'name': 'Mint Green Casual Tee', 'description': 'Fresh mint green t-shirt with modern fit. Perfect for everyday wear.', 'category': 'womens', 'regular_price': Decimal('899.00'), 'offer_price': Decimal('699.00'), 'stock': 55},
            {'name': 'Black Fitted Premium Tee', 'description': 'Sleek black fitted t-shirt with premium quality fabric.', 'category': 'womens', 'regular_price': Decimal('949.00'), 'offer_price': None, 'stock': 75},
            {'name': 'Rose Gold Elegant Tee', 'description': 'Elegant rose gold t-shirt with sophisticated design.', 'category': 'womens', 'regular_price': Decimal('999.00'), 'offer_price': Decimal('799.00'), 'stock': 45},
            {'name': 'Sky Blue Comfort Fit Tee', 'description': 'Comfortable sky blue t-shirt with relaxed fit. Perfect for casual days.', 'category': 'womens', 'regular_price': Decimal('829.00'), 'offer_price': None, 'stock': 80},
            {'name': 'Peach Soft Cotton T-Shirt', 'description': 'Soft peach colored t-shirt made from premium cotton.', 'category': 'womens', 'regular_price': Decimal('899.00'), 'offer_price': Decimal('699.00'), 'stock': 65},
            {'name': 'Navy Blue Classic Women\'s Tee', 'description': 'Classic navy blue t-shirt with timeless design. Versatile and stylish.', 'category': 'womens', 'regular_price': Decimal('949.00'), 'offer_price': None, 'stock': 50},
            
            # Combo Products (10)
            {'name': 'Couple\'s Matching Black Tee Set', 'description': 'Matching black t-shirt set for couples. Perfect for matching outfits.', 'category': 'combo', 'regular_price': Decimal('1699.00'), 'offer_price': Decimal('1299.00'), 'stock': 30},
            {'name': 'Family Pack White Tees (2 Pieces)', 'description': 'Two-piece white t-shirt combo pack. Great value for families.', 'category': 'combo', 'regular_price': Decimal('1599.00'), 'offer_price': None, 'stock': 40},
            {'name': 'Premium Combo Pack - Navy & Gray', 'description': 'Premium combo pack with navy and gray t-shirts. Best value deal.', 'category': 'combo', 'regular_price': Decimal('1799.00'), 'offer_price': Decimal('1399.00'), 'stock': 25},
            {'name': 'Summer Combo - Pink & Coral', 'description': 'Summer combo pack with pink and coral t-shirts. Perfect for warm weather.', 'category': 'combo', 'regular_price': Decimal('1699.00'), 'offer_price': None, 'stock': 35},
            {'name': 'Classic Combo - Black & White', 'description': 'Classic combo with black and white t-shirts. Essential wardrobe pieces.', 'category': 'combo', 'regular_price': Decimal('1749.00'), 'offer_price': Decimal('1399.00'), 'stock': 45},
            {'name': 'Couple\'s Valentine Set - Red & Pink', 'description': 'Romantic couple\'s set with red and pink t-shirts. Perfect for special occasions.', 'category': 'combo', 'regular_price': Decimal('1899.00'), 'offer_price': None, 'stock': 20},
            {'name': 'Premium Mix Combo (3 Pieces)', 'description': 'Premium three-piece combo pack. Great variety and value.', 'category': 'combo', 'regular_price': Decimal('2499.00'), 'offer_price': Decimal('1999.00'), 'stock': 15},
            {'name': 'Casual Combo - Gray & Beige', 'description': 'Casual combo pack with gray and beige t-shirts. Comfortable everyday wear.', 'category': 'combo', 'regular_price': Decimal('1699.00'), 'offer_price': None, 'stock': 30},
            {'name': 'Vibrant Combo - Blue & Green', 'description': 'Vibrant combo pack with blue and green t-shirts. Stand out in style.', 'category': 'combo', 'regular_price': Decimal('1799.00'), 'offer_price': Decimal('1499.00'), 'stock': 28},
            {'name': 'Best Value Combo Pack', 'description': 'Best value combo pack with premium quality t-shirts. Limited stock available.', 'category': 'combo', 'regular_price': Decimal('1999.00'), 'offer_price': None, 'stock': 22},
        ]

        created_count = 0
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                name=product_data['name'],
                defaults={
                    'description': product_data['description'],
                    'category': product_data['category'],
                    'regular_price': product_data['regular_price'],
                    'offer_price': product_data['offer_price'],
                    'stock': product_data['stock'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created: {product.name} ({product.category})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Skipped (already exists): {product.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} new products!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Total products in database: {Product.objects.count()}')
        )

