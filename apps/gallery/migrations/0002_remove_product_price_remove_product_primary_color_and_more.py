# Generated by Django 5.1.4 on 2025-01-25 18:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="price",
        ),
        migrations.RemoveField(
            model_name="product",
            name="primary_color",
        ),
        migrations.AddField(
            model_name="product",
            name="base_price",
            field=models.FloatField(
                blank=True,
                default=0,
                help_text="Variant pricing will override this.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="height",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="height_unit",
            field=models.CharField(
                blank=True,
                choices=[("IN", "Inches"), ("CM", "Centimeters")],
                default="IN",
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="length",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="length_unit",
            field=models.CharField(
                blank=True,
                choices=[("IN", "Inches"), ("CM", "Centimeters")],
                default="IN",
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="weight",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="weight_unit",
            field=models.CharField(
                blank=True,
                choices=[
                    ("LB", "Pounds"),
                    ("OZ", "Ounces"),
                    ("G", "Grams"),
                    ("KG", "Kilograms"),
                ],
                default="OZ",
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="width",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="width_unit",
            field=models.CharField(
                blank=True,
                choices=[("IN", "Inches"), ("CM", "Centimeters")],
                default="IN",
                max_length=10,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="productimage",
            name="modified_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="productimage",
            name="resource_url",
            field=models.URLField(
                blank=True,
                help_text="Shopify resourceURL if uploaded to Shopify",
                max_length=500,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="shopify_global_id",
            field=models.CharField(
                blank=True,
                editable=False,
                help_text="Shopify Global productID",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="shopify_sync",
            field=models.BooleanField(
                default=False,
                help_text="Enable to automatically sync product with Shopify Admin.  Please note, updates made in Shopify Admin will be overridden, and do not sync with the product database. A Shopify Access Token is required!",
                verbose_name="Enable ShopSync",
            ),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="feature_image",
            field=models.BooleanField(
                default=False,
                help_text="Enable to display image as the featured image. The featured image is used as the product's primary image",
            ),
        ),
        migrations.CreateModel(
            name="ProductOption",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("position", models.IntegerField()),
                (
                    "name",
                    models.CharField(
                        help_text='e.g. "Color" or "Pattern"',
                        max_length=100,
                        verbose_name="Option Name",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gallery.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ProductOptionValue",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                (
                    "value",
                    models.CharField(max_length=100, verbose_name="Option Value"),
                ),
                (
                    "option",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gallery.productoption",
                        verbose_name="Option Name",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="productoption",
            name="values",
            field=models.ManyToManyField(
                blank=True,
                help_text='Values for this Option (e.g. "Red", "Blue", etc.',
                to="gallery.productoptionvalue",
                verbose_name="Option Values",
            ),
        ),
        migrations.CreateModel(
            name="ProductVariant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("shopify_id", models.CharField(blank=True, max_length=100)),
                (
                    "inv_policy",
                    models.CharField(
                        choices=[("DENY", "Deny"), ("CONTINUE", "Continue")],
                        default="DENY",
                        help_text="When a product has no inventory available, this policy determines if new orders should continue to process, or be denied.",
                        max_length=100,
                        verbose_name="Inventory Policy",
                    ),
                ),
                ("sku", models.CharField(blank=True, max_length=100)),
                (
                    "location",
                    models.CharField(max_length=100, verbose_name="Inventory Location"),
                ),
                (
                    "oh_quantity",
                    models.IntegerField(default=1, verbose_name="On Hand Quantity"),
                ),
                ("price", models.FloatField(default=0, verbose_name="Variant Price")),
                (
                    "inv_name",
                    models.CharField(
                        choices=[("available", "Available"), ("on hand", "On Hand")],
                        default="available",
                        max_length=100,
                        verbose_name="Inventory Name",
                    ),
                ),
                (
                    "options",
                    models.ManyToManyField(
                        blank=True,
                        to="gallery.productoptionvalue",
                        verbose_name="Options",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gallery.product",
                    ),
                ),
            ],
        ),
    ]
