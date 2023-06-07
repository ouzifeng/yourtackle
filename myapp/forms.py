from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Brand, Category, Product, TackleShop, Offer, ProductImage
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.core.exceptions import ValidationError


class YourForm(forms.Form):
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "list": "brands"}),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=True,
        widget=forms.Select(attrs={"class": "form-control", "list": "categories"}),
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        phone_number = self.cleaned_data["phone_number"]
        if commit:
            user.save()
            profile = Profile(user=user, phone_number=phone_number)
            profile.save()
        return user


class ProductForm(forms.ModelForm):
    confirm = forms.BooleanField(required=True, label="I confirm that all information given is true. Failure to do so may impact the final price when it arrives with the buyer")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control"
            visible.field.widget.attrs["placeholder"] = visible.label

    def clean_confirm(self):
        confirm = self.cleaned_data.get('confirm')
        if not confirm:
            raise ValidationError("You must agree to the confirmation.")
        return confirm

    class Meta:
        model = Product
        fields = (
            "brand",
            "category",
            "name",
            "variation1",
            "variation2",
            "condition",
            "description",
            "confirm",
            # "photos",
            # "photos2",
            # "photos3",
            # "photos4",
        )


class ProductImageForm(forms.ModelForm):
    image = forms.ImageField(label="Image")

    class Meta:
        model = ProductImage
        fields = ("image",)


class RegistrationForm(UserCreationForm):
    user_type = forms.ChoiceField(choices=Profile.USER_TYPE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + (
            "email",
            "user_type",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.profile.user_type = self.cleaned_data["user_type"]
            user.profile.save()
        return user


class UserRegisterForm(UserCreationForm):
    ROLE_CHOICES = [
        ("seller", "Sell - I want to sell tackle"),
        ("buyer", "Tackle shop - I want to buy tackle"),
    ]

    email = forms.EmailField()
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    phone_number = forms.CharField(max_length=20)  # This field is added here

    class Meta:
        model = User
        fields = [
            "role",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password1",
            "password2",
        ]

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            profile = Profile(
                user=user,
                phone_number=self.cleaned_data["phone_number"],
                user_type=self.cleaned_data["role"],
            )  # create profile instance
            profile.save()
        return user


class TackleShopRegistrationForm(forms.ModelForm):
    shop_url = forms.CharField()

    class Meta:
        model = TackleShop
        fields = [
            "shop_name",
            "shop_url",
            "shop_logo",
            "address_line1",
            "city",
            "county",
            "postcode",
        ]

    def clean_shop_url(self):
        url = self.cleaned_data["shop_url"]
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        return url

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Register Tackle Shop"))


class TackleShopForm(forms.ModelForm):
    class Meta:
        model = TackleShop
        fields = ["shop_name", "shop_url"]  # include the fields you want to update here


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["cash_price", "trade_in_price", "insurance_included"]

