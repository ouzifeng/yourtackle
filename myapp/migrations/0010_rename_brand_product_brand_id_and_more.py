# Generated by Django 4.2 on 2023-05-23 17:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0009_alter_product_id"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="brand",
            new_name="brand_id",
        ),
        migrations.RenameField(
            model_name="product",
            old_name="category",
            new_name="category_id",
        ),
    ]
