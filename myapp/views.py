from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import (
    YourForm,
    CustomUserCreationForm,
    UserRegisterForm,
    ProductForm,
    TackleShopRegistrationForm,
    TackleShopForm,
    OfferForm,
    ProductImageForm,
    ContactForm,
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import (
    Brand,
    Category,
    Condition,
    Product,
    ProductImage,
    Profile,
    TackleShop,
    Offer,
)
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import HttpResponse
from django.core.mail import mail_admins, send_mail
from django.contrib.auth.models import User


def index(request):
    return render(request, "index.html")


def contact_view(request):
    return render(request, "contact.html")


def about(request):
    return render(request, "about.html")


def faq(request):
    return render(request, "faq.html")


def pricing(request):
    return render(request, "pricing.html")


def blog(request):
    return render(request, "blog.html")


def bloghome(request):
    return render(request, "bloghome.html")


def form_view(request):
    return render(request, "form.html")


def portfoliooverview(request):
    return render(request, "portfolio-overview.html")


def portfolioitem(request):
    return render(request, "portfolio-item.html")


def myaccount(request):
    return render(request, "my-account.html")


def product(request):
    return render(request, "product.html")


def tackleshopaccount(request):
    return render(request, "tackle-shop-account.html")

def howitworks(request):
    return render(request, "how-it-works.html")


def custom_logout(request):
    logout(request)
    return redirect("index")


def role_required(required_role):
    """Requires that the logged in user has a specific role."""

    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            profile = Profile.objects.get(user=request.user)
            if not profile.user_type == required_role:
                raise PermissionDenied  # can also redirect to a 403 page
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@role_required("seller")
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                messages.success(request, "You have been logged in")
                login(request, user)
                return redirect("myaccount")
            else:
                print("Incorrect password")
        except User.DoesNotExist:
            print("User does not exist")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


@role_required("buyer")
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                messages.success(request, "You have been logged in")
                login(request, user)
                return redirect("tackleshopaccount")
            else:
                print("Incorrect password")
        except User.DoesNotExist:
            print("User does not exist")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def register(request):
    if request.user.is_authenticated:
        return redirect("index")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data["role"]
            user.profile.user_type = role
            user.profile.save()  # save the user_type to the profile
            auth_user = authenticate(
                request, username=user.username, password=request.POST["password1"]
            )
            if auth_user is not None:
                login(request, auth_user)
                messages.success(
                    request, "You have been successfully registered and logged in."
                )
                if role == "seller":
                    return redirect("product")  # redirect to product page
                elif role == "buyer":
                    return redirect(
                        "tackle-shop-register"
                    )  # redirect to tackle shop registration page
            else:
                messages.error(request, "Authentication failed.")
    else:
        form = UserRegisterForm()
    return render(request, "register.html", {"form": form})



def form_view(request):
    if request.user.is_authenticated:
        return redirect("product")
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_user = authenticate(
                request, username=user.email, password=request.POST["password1"]
            )
            if auth_user is not None:
                login(request, auth_user)
                messages.success(
                    request, "You have been successfully registered and logged in."
                )
                return redirect("product")  # redirect to product page
            else:
                messages.error(request, "Authentication failed.")
    else:
        form = CustomUserCreationForm()
    return render(request, "form.html", {"form": form})


@login_required
def product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        product_image_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid() and product_image_form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()

            # save each image file
            for f in request.FILES.getlist("image"):
                ProductImage.objects.create(product=product, image=f)

            return redirect("myaccount")
        else:
            print(form.errors)
    else:
        form = ProductForm()
        product_image_form = ProductImageForm()
    return render(
        request,
        "product.html",
        {"form": form, "product_image_form": product_image_form},
    )


@role_required("seller")
def myaccount(request):
    user_products = Product.objects.filter(user=request.user).order_by("-created_at")

    product_data = []
    for product in user_products:
        offers = Offer.objects.filter(product=product)
        offer_count = offers.count()
        offer_text = 'offer' if offer_count == 1 else 'offers'

        accepted_offers = offers.filter(status=Offer.OfferStatus.ACCEPTED).exists()
        product_offer_status = "accepted" if accepted_offers else "pending"

        product_detail = {
            "product": product,
            "offer_count": offer_count,
            "product_offer_status": product_offer_status,
            "product_images": product.images.all(),  # Assuming 'images' is a related_name for the images
        }

        product_data.append(product_detail)

    return render(request, "my-account.html", {"product_data": product_data})


@login_required
@role_required("seller")
def view_offers(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_images = ProductImage.objects.filter(product=product)
    offers = Offer.objects.filter(product=product).order_by("-cash_price") #Changed here
    accepted_offer = Offer.objects.filter(
        product=product, status=Offer.OfferStatus.ACCEPTED
    ).first()
    is_offer_accepted = bool(accepted_offer)

    return render(
        request,
        "view-offer.html",
        {
            "product": product,
            "offers": offers,
            "product_images": product_images,
            "accepted_offer": accepted_offer,
            "accepted_offer_price": accepted_offer.cash_price
            if accepted_offer
            else None,  # Add the accepted offer price
            "is_offer_accepted": is_offer_accepted,
        },
    )





@login_required
@role_required("buyer")
def tackleshopaccount(request):
    filter = request.GET.get("filter", "all")
    tackle_shop = TackleShop.objects.get(user=request.user)
    # Adjust the products loaded based on the filter
    if filter == "offer_made":
        products = Product.objects.filter(offer_set__buyer=request.user).order_by('-created_at')
    elif filter == "offer_accepted":
        products = Product.objects.filter(
            offer_set__buyer=request.user, offer_set__status=Offer.OfferStatus.ACCEPTED
        ).order_by('-created_at')
    else:
        products = (
            Product.objects.all().order_by('-created_at')
        )  # Fetch all products if no filter or 'all' is selected

    # Build a list of dictionaries containing product and offer data
    product_data = []
    for product in products:
        offers = product.offer_set.filter(buyer=request.user)
        offer_count = offers.count()

        if offer_count == 1:
            offer_text = "Offer"
        else:
            offer_text = "Offers"

        # Check offer status for the tackle shop's offer
        offer = None
        offer_status = None
        for offer in offers:
            if offer.status == Offer.OfferStatus.ACCEPTED:
                offer_status = "Offer Accepted"
                break
            elif offer.status == Offer.OfferStatus.REJECTED:
                offer_status = "Offer Rejected"
                break
            elif offer.status == Offer.OfferStatus.PENDING:
                offer_status = "Offer Pending"
                break

        if (
            not offer_status
            and product.offer_set.filter(status=Offer.OfferStatus.ACCEPTED).exists()
        ):
            offer_status = "Already Sold"

        product_data.append(
            {
                "product": product,
                "offer": offer,
                "offer_count": offer_count,
                "offer_text": offer_text,
                "offer_status": offer_status,
            }
        )

    if request.method == "POST":
        form = TackleShopForm(request.POST, instance=tackle_shop)
        if form.is_valid():
            form.save()
    else:
        form = TackleShopForm(instance=tackle_shop)

    context = {"product_data": product_data, "tackle_shop": tackle_shop}
    return render(request, "tackle-shop-account.html", context)


def tackleshopregister(request):
    if request.method == "POST":
        form = TackleShopRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            tackle_shop = form.save(commit=False)
            tackle_shop.user = request.user
            tackle_shop.save()
            return redirect(
                "tackleshopaccount"
            )  # Redirect to the tackle shop's account page
        else:
            print(form.errors)
    else:
        form = TackleShopRegistrationForm()

    return render(request, "tackle-shop.html", {"form": form})


def role_required(required_role):
    """Requires that the logged in user has a specific role."""

    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            profile = Profile.objects.get(user=request.user)
            if not profile.user_type == required_role:
                raise PermissionDenied  # can also redirect to a 403 page
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@login_required
@role_required("buyer")
def make_offer(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    seller_user = User.objects.get(id=product.user_id)  # Get user from user_id in Product model
    seller_profile = seller_user.profile  # Get user's profile
    seller = {
        'first_name': seller_user.first_name,
        'last_name': seller_user.last_name,
        'email': seller_user.email,
        'phone_number': seller_profile.phone_number
    }

    existing_offer = Offer.objects.filter(buyer=request.user, product=product).first()
    if request.method == "POST":
        if existing_offer:
            messages.error(request, "You have already made an offer for this product.")
            return redirect("tackleshopaccount")

        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.buyer = request.user
            offer.product = product
            offer.save()
            messages.success(request, "Offer submitted successfully.")
            return redirect("tackleshopaccount")
    else:
        form = OfferForm()
        return render(
        request,
        "make-offer.html",
        {
            "product": product,
            "form": form,
            "existing_offer": existing_offer,
            "cash_price": str(existing_offer.cash_price) if existing_offer else None,
            "trade_in_price": str(existing_offer.trade_in_price) if existing_offer else None,
            "seller": seller,  # Pass the seller data to the template
        },
    )



@login_required
def accept_offer(request, offer_id):
    if request.method == "POST":
        offer = get_object_or_404(Offer, id=offer_id)
        with transaction.atomic():
            offer.status = Offer.OfferStatus.ACCEPTED
            offer.save()

            # Set other offers for this product to Rejected
            Offer.objects.filter(product=offer.product).exclude(id=offer.id).update(
                status=Offer.OfferStatus.REJECTED
            )

        return redirect("myaccount")
   
    
class OffersAccepted(View):
    def get(self, request):
        offers = Offer.objects.filter(buyer=request.user, status='ACCEPTED').order_by('-product__created_at')
        
        # Extract the products from the offers
        products = [offer.product for offer in offers]
        
        # Retrieve tackle_shop based on your database structure
        tackle_shop = request.user.tackleshop  # Replace with your actual code

        return render(request, "offers_accepted.html", {"offers": offers, "products": products, "tackle_shop": tackle_shop})



class OffersMade(View):
    def get(self, request):
        offers = Offer.objects.filter(buyer=request.user, status='PENDING').order_by('-product__created_at')
        
        offer_data = [{'product': offer.product, 'offer': offer} for offer in offers]
        
        print(offer_data)  # print statement to check the offer_data
        
        tackle_shop = request.user.tackleshop  # Replace with your actual code
        
        return render(request, "offers_made.html", {"offer_data": offer_data, "tackle_shop": tackle_shop})

    
class ProductsForSale(LoginRequiredMixin, View):
    def get(self, request):
        user_offers = Offer.objects.filter(buyer=request.user).values_list('product_id', flat=True)
        accepted_offers = Offer.objects.filter(status='accepted').values_list('product_id', flat=True)
        products = Product.objects.exclude(id__in=user_offers).exclude(id__in=accepted_offers).order_by('-created_at')
        
        # Retrieve tackle_shop based on your database structure
        tackle_shop = request.user.tackleshop  # Replace with your actual code
        
        return render(request, "products_for_sale.html", {"products": products, "tackle_shop": tackle_shop})

  

@login_required
@role_required("seller")
def seller_offers_made(request):
    user_products = Product.objects.filter(user=request.user).order_by("-created_at")
    offer_data = []

    for product in user_products:
        offers = Offer.objects.filter(product=product, status='PENDING')
        if offers.exists():
            offer_count = offers.count()
            offer_text = "Offer" if offer_count == 1 else "Offers"
            offer_data.append({
                "product": product,
                "offers": offers,
                "offer_count": offer_count,
                "offer_text": offer_text,
            })

    return render(request, "seller-offers-made.html", {"offer_data": offer_data})


@login_required
@role_required("seller")
def seller_offers_accepted(request):
    user_products = Product.objects.filter(user=request.user).order_by("-created_at")
    offer_data = []

    for product in user_products:
        offers = Offer.objects.filter(product=product, status='ACCEPTED')
        if offers.exists():
            offer_count = offers.count()
            offer_text = "Offer" if offer_count == 1 else "Offers"
            offer_data.append({
                "product": product,
                "offers": offers,
                "offer_count": offer_count,
                "offer_text": offer_text,
            })

    return render(request, "seller-offers-accepted.html", {"offer_data": offer_data})

def edit_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    image = product.images.first()  # Get the first image of the product
    print(f'Editing product with ID {product_id}')  # Add this line

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES, instance=image)

        if form.is_valid() and image_form.is_valid():
            form.save()
            image_form.save()
            print(f'Saved changes, redirecting to product with ID {product.id}')  # Add this line
            return redirect('edit_product', product_id=product.id)
        else:
            print('Form is not valid')  # Add this line
    else:
        form = ProductForm(instance=product)
        image_form = ProductImageForm(instance=image)

    return render(request, 'edit_product.html', {'form': form, 'image_form': image_form})


@login_required
@role_required("seller")
def delete_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.user.id != product.user_id:
        messages.error(request, "You don't have permission to delete this product.")
        return redirect(reverse('myaccount'))

    # Query the Offer model for accepted offers on this product
    offer_accepted = Offer.objects.filter(product=product, status=Offer.OfferStatus.ACCEPTED).exists()

    if offer_accepted:
        messages.error(request, "Can't delete this product. An offer has been accepted on it.")
        return redirect(reverse('myaccount'))

    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect(reverse('myaccount'))

def index(request):
    print("Inside landing_page view")
    offers = Offer.objects.filter(status=Offer.OfferStatus.ACCEPTED)  # Update this to match your accepted status
    products_with_offers = [{'product': offer.product, 'price': offer.trade_in_price or offer.cash_price} for offer in offers]
    print(f'Found {len(products_with_offers)} products with accepted offers')
    return render(request, 'index.html', {'products_with_offers': products_with_offers})

def robots_txt(request):
    lines = [
        "User-Agent: *",
        # Add any other url you want to hide from web crawlers
        "Sitemap: https://www.sellyourtackle.co.uk/sitemap.xml"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            message = form.cleaned_data.get('message')

            subject = f'Message from {name}'
            message = f'From: {name}\nE-mail: {email}\nPhone: {phone}\n\n{message}'

            mail_admins(subject, message)

            # Add success message or redirect here

    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            phone = form.cleaned_data.get('phone')
            message = form.cleaned_data.get('message')

            subject = f'Message from {name}'
            message = f'From: {name}\nE-mail: {email}\nPhone: {phone}\n\n{message}'

            send_mail(
                subject,
                message,
                'Sell Your Tackle <hello@sellyourtackle.co.uk>',  # This is the sender
                ['hello@sellyourtackle.co.uk'],  # This is the recipient
            )

            messages.success(request, 'Thanks for your message! We will get back to you as soon as possible.')
            
            # Redirect back to the same page after the form is successfully submitted
            return redirect(request.path_info)
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
