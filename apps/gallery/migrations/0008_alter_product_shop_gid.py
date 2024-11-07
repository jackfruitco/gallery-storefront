# Generated by Django 5.1.2 on 2024-11-07 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0007_product_shop_gid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='shop_GID',
            field=models.CharField(blank=True, editable=False, help_text='Shopify productID', max_length=100),
        ),
    ]
