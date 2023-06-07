from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Brand(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "myapp_categories"

    def __str__(self):
        return self.name


class Condition(models.TextChoices):
    PERFECT = "Perfect", "Perfect - never been used and no blemishes"
    EXCELLENT = "Excellent", "Excellent- a few minor cosmetic issues"
    GOOD = "Good", "Good - some dings and scratches"
    FAIR = "Fair", "Fair - extensive cosmetic issues"

    def __str__(self):
        return f"{self.label} {self.additional_info}"


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    variation1 = models.CharField(max_length=100, blank=True, null=True)
    variation2 = models.CharField(max_length=100, blank=True, null=True)
    condition = models.CharField(max_length=100, choices=Condition.choices)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # photos = models.ImageField(upload_to="images")
    # photos2 = models.ImageField(upload_to="images", blank=True, null=True)
    # photos3 = models.ImageField(upload_to="images", blank=True, null=True)
    # photos4 = models.ImageField(upload_to="images", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Product id: {str(self.id)}, name: {self.name}, brand: {self.brand.name}, category: {self.category.name}, condition: {self.condition}"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return str(self.id)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone_number = models.CharField(
        max_length=20, null=True
    )  # add null=True if you want to allow empty phone_number
    USER_TYPE_CHOICES = (
        ("seller", "Seller"),
        ("buyer", "Buyer"),
    )
    user_type = models.CharField(max_length=6, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class TackleShop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=200)
    shop_url = models.URLField()
    shop_logo = models.ImageField(upload_to="shop_logos")
    address_line1 = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    county = models.CharField(max_length=200)
    postcode = models.CharField(max_length=20)

    def __str__(self):
        return self.shop_name


class Offer(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cash_price = models.DecimalField(max_digits=6, decimal_places=2)
    trade_in_price = models.DecimalField(max_digits=6, decimal_places=2)
    insurance_included = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class OfferStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    status = models.CharField(
        max_length=20,
        choices=OfferStatus.choices,
        default=OfferStatus.PENDING,
    )

