# Generated by Django 5.1.2 on 2024-12-06 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='options',
            field=models.ManyToManyField(blank=True, to='gallery.productoptionvalue', verbose_name='Options'),
        ),
    ]
