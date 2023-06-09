# Generated by Django 4.2 on 2023-05-23 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0012_product_name_productimage"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="photos",
            field=models.ImageField(upload_to="products/"),
        ),
        migrations.AlterField(
            model_name="productimage",
            name="image",
            field=models.ImageField(upload_to="product_images/"),
        ),
    ]
