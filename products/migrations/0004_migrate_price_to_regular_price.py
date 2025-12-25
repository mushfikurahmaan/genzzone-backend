# Generated migration to copy price to regular_price

from django.db import migrations


def migrate_price_to_regular_price(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        if product.price and not product.regular_price:
            product.regular_price = product.price
            product.save()


def reverse_migration(apps, schema_editor):
    # Reverse migration - copy regular_price back to price if needed
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        if product.regular_price and not product.price:
            product.price = product.regular_price
            product.save()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_offer_price_product_regular_price_and_more'),
    ]

    operations = [
        migrations.RunPython(migrate_price_to_regular_price, reverse_migration),
    ]

