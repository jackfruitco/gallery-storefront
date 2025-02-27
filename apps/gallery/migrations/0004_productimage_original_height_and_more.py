# Generated by Django 5.1.6 on 2025-02-17 20:36

from django.db import migrations, models

import apps.gallery.models


class Migration(migrations.Migration):

    dependencies = [
        ("gallery", "0003_rename_image_productimage_original"),
    ]

    operations = [
        migrations.AddField(
            model_name="productimage",
            name="original_height",
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name="productimage",
            name="original_width",
            field=models.PositiveIntegerField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="original",
            field=models.ImageField(
                height_field="original_height",
                upload_to=apps.gallery.models.get_image_path,
                width_field="original_width",
            ),
        ),
    ]
