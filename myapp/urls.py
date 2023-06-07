from django.urls import path, include
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import accept_offer, ProductsForSale, delete_product

urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", views.contact_view, name="contact"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("pricing/", views.pricing, name="pricing"),
    path("blog/", views.blog, name="blog"),
    path("bloghome/", views.bloghome, name="bloghome"),
    path("portfolio-overview/", views.portfoliooverview, name="portfoliooverview"),
    path("portfolio-item/", views.portfolioitem, name="portfolioitem"),
    path("form/", views.form_view, name="form_view"),
    path("register/", views.register, name="register"),
    path("login/", LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="index"), name="logout"),
    path("my-account/", views.myaccount, name="myaccount"),
    path("product/", views.product, name="product"),
    path(
        "tackle-shop-register/", views.tackleshopregister, name="tackle-shop-register"
    ),
    path("tackle-shop-account/", views.tackleshopaccount, name="tackleshopaccount"),
    path("social/", include("social_django.urls", namespace="social")),
    path("product/<int:product_id>/offer/", views.make_offer, name="make_offer"),
    path("product/<int:product_id>/offers/", views.view_offers, name="view_offers"),
    path("view-offers/<int:product_id>/", views.view_offers, name="view_offers"),
    path("accept_offer/<int:offer_id>/", accept_offer, name="accept_offer"),
    path('tackle-shop-account/products-for-sale/', ProductsForSale.as_view(), name='products_for_sale'),
    path('tackle-shop-account/offersaccepted/', views.OffersAccepted.as_view(), name='offers_accepted'),
    path('tackle-shop-account/offersmade/', views.OffersMade.as_view(), name='offers_made'),
    path('myaccount/seller-offers-made/', views.seller_offers_made, name='seller_offers_made'),
    path('myaccount/seller-offers-accepted/', views.seller_offers_accepted, name='seller_offers_accepted'),
    path('product/edit/<int:product_id>', views.edit_product, name='edit_product'),
    path('product/delete/<int:product_id>', delete_product, name='delete_product'),
]

if settings.DEBUG:  # new
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
