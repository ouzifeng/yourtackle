# Generated by Django 4.2 on 2023-05-27 20:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0030_product_photos2_product_photos3_product_photos4"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="product",
            name="photos",
        ),
        migrations.RemoveField(
            model_name="product",
            name="photos2",
        ),
        migrations.RemoveField(
            model_name="product",
            name="photos3",
        ),
        migrations.RemoveField(
            model_name="product",
            name="photos4",
        ),
    ]
