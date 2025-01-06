# Generated by Django 5.1.2 on 2025-01-03 00:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_remove_product_price_product_base_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='feature',
            field=models.BooleanField(default=True, help_text='Enable to display this product on the Homepage as a featured product.', verbose_name='Enable Featured Product'),
        ),
        migrations.AlterField(
            model_name='product',
            name='shopify_sync',
            field=models.BooleanField(default=False, help_text='Enable to automatically sync product with Shopify Admin.  Please note, updates made in Shopify Admin will be overridden, and do not sync with the product database. A Shopify Access Token is required!', verbose_name='Enable ShopSync'),
        ),
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('ARCHIVED', 'Archived')], default='ACTIVE', help_text='Enable to display this product in Site Gallery', max_length=10, verbose_name='Enable Site Gallery'),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='feature_image',
            field=models.BooleanField(default=False, help_text="Enable to display image as the featured image. The featured image is used as the product's primary image"),
        ),
    ]
