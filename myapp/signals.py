from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, pre_save
from django.conf import settings
import threading
from django.core.mail import EmailMessage
from .models import Product, Offer
from myapp.models import Profile
from django.urls import reverse
from django.contrib.auth.models import User

def send_async_email(email):
    email.send()

   
@receiver(post_save, sender=get_user_model())
def send_registration_email(sender, instance=None, created=False, **kwargs):
    if created:  # Check if the User instance was created
        subject = "Welcome to Sell Your Tackle"
        body = f"""
        Hi {instance.first_name},<br><br>

        Thanks for joining Sell Your Tackle, the UK's fastest growing used fishing tackle marketplace. Your account is now setup and all ready to go. To login please visit <a href="https://www.sellyourtackle.co.uk/login" target="_blank">HERE</a><br><br>

        You can read more about what we do <a href="https://www.sellyourtackle.co.uk/FAQ" target="_blank">HERE</a><br><br>

        Tight Lines,<br>
        The Sell Your Tackle Team
        """
        email = EmailMessage(subject, body, settings.FROM_EMAIL, [instance.email])
        email.content_subtype = 'html'  # Here is the correct way to set the content_subtype
        threading.Thread(target=send_async_email, args=(email,)).start()




@receiver(post_save, sender=Product)
def send_product_listed_email(sender, instance=None, created=False, **kwargs):
    if created:  # Check if the Product instance was created
        subject = "Product Listed Successfully"
        body = f"""
        Hi {instance.user.first_name},<br><br>

        Thanks for listing your {instance.name} on Sell Your Tackle. All the buyers on the website have now been invited to bid on it.<br><br>

        All you need to do now is wait. You will be notified once a buyer makes you an offer.<br><br>

        Best of luck<br>
        The Sell Your Tackle Team
        """
        email = EmailMessage(subject, body, settings.FROM_EMAIL, [instance.user.email])  # use user attribute here
        email.content_subtype = 'html'  # Here is the correct way to set the content_subtype
        threading.Thread(target=send_async_email, args=(email,)).start()


@receiver(post_save, sender=Product)
def send_product_listed_email(sender, instance=None, created=False, **kwargs):
    if created:  # Check if the Product instance was created
        subject = "New Product Listed"
        buyers = Profile.objects.filter(user_type='buyer') # This gets all buyers from Profile model
        
        for buyer in buyers:
            body = f"""
            Hi {buyer.user.first_name},<br><br>

            A new product has been listed on Sell Your Tackle. We thought you might be interested. Please visit our website to check it out.<br><br>

            Best regards,<br>
            The Sell Your Tackle Team
            """
            email = EmailMessage(subject, body, settings.FROM_EMAIL, [buyer.user.email], headers = {'Content-Type': 'text/html'})
            threading.Thread(target=send_async_email, args=(email,)).start()
            
            
@receiver(post_save, sender=Product)
def send_product_listed_email(sender, instance=None, created=False, **kwargs):
    if created:  # Check if the Product instance was created
        buyers = Profile.objects.filter(user_type='buyer')
        for buyer in buyers:
            product_url = f"https://www.sellyourtackle.co.uk{reverse('make_offer', args=[instance.id])}"
            subject = "New Product Listed on Sell Your Tackle"
            html_content = f"""
            Hi {buyer.user.first_name},<br><br>
            
            A new product has been listed on Sell Your Tackle and we thought you might be interested.<br><br>

            Name: {instance.name}<br>
            Condition: {instance.condition}<br>
            You can view and make an offer on the product <a href="{product_url}">HERE</a>.<br><br>
            
            Best of luck<br>
            The Sell Your Tackle Team
            """
            text_content = strip_tags(html_content)  # this strips the html, so people will have the text as well.
            
            # create the email, and attach the HTML version as well as the text version.
            email = EmailMultiAlternatives(subject, text_content, settings.FROM_EMAIL, [buyer.user.email])
            email.attach_alternative(html_content, "text/html")
            threading.Thread(target=email.send, args=()).start()          
            
@receiver(post_save, sender=Offer)
def send_new_offer_email(sender, instance=None, created=False, **kwargs):
    if created:  # Check if the Offer instance was created
        seller = User.objects.get(id=instance.product.user_id)  # Get seller from user_id in Product model
        offer_url = f"https://www.sellyourtackle.co.uk{reverse('view_offers', args=[instance.product.id])}"
        subject = "New offer on Sell Your Tackle"
        html_content = f"""
        Hi {seller.first_name},<br><br>
        
        A new offer has been made on your product: {instance.product.name}<br>

        You can view the offer <a href="{offer_url}">HERE</a>.<br><br>
        
        Best of luck<br>
        The Sell Your Tackle Team
        """
        text_content = strip_tags(html_content)  # this strips the html, so people will have the text as well.
        
        # create the email, and attach the HTML version as well as the text version.
        email = EmailMultiAlternatives(subject, text_content, settings.FROM_EMAIL, [seller.email])
        email.attach_alternative(html_content, "text/html")
        email.send()     
        
        
@receiver(pre_save, sender=Offer)
def send_offer_accepted_email(sender, instance=None, **kwargs):
    if instance.pk:  # Check if this is an update
        old_offer = Offer.objects.get(pk=instance.pk)
        if old_offer.status != instance.status and instance.status == Offer.OfferStatus.ACCEPTED:
            # Status changed to accepted, send emails
            # Send email to buyer
            buyer = instance.buyer
            product = instance.product
            seller = User.objects.get(id=product.user_id)  # Get seller from user_id in Product model

            product_url = f"https://www.sellyourtackle.co.uk{reverse('make_offer', args=[product.id])}"

            subject_to_buyer = "Congratulations, your offer has been accepted!"
            html_content_to_buyer = f"""
            Hi {buyer.first_name},<br><br>
            
            Congratulations, your offer on {product.name} has been accepted. Please contact the seller at your earliest convenience on the following email or phone number.<br>
            Seller Name: {seller.first_name} {seller.last_name}<br>
            Seller Email: {seller.email}<br>
            Seller Phone Number: {seller.profile.phone_number}<br><br>
            
            Ask them whether they prefer the cash price or the trade-in price. To view the product, click <a href="{product_url}">HERE</a>.<br><br>

            An email has been sent to {seller.first_name} to let them know you will be contacting them as soon as possible to arrange pickup.<br><br>

            Best of luck,<br>
            The Sell Your Tackle Team
            """
            text_content_to_buyer = strip_tags(html_content_to_buyer)  # this strips the html, so people will have the text as well.
            
            # create the email, and attach the HTML version as well as the text version.
            email_to_buyer = EmailMultiAlternatives(subject_to_buyer, text_content_to_buyer, settings.FROM_EMAIL, [buyer.email])
            email_to_buyer.attach_alternative(html_content_to_buyer, "text/html")
            threading.Thread(target=send_async_email, args=(email_to_buyer,)).start()

            # Send email to seller
            subject_to_seller = "You've accepted an offer!"
            html_content_to_seller = f"""
            Hi {seller.first_name},<br><br>
            
            Congratulations on accepting the offer for {product.name}.<br><br>

            The buyer's information is as follows:<br>
            Buyer Name: {buyer.first_name} {buyer.last_name}<br>
            Buyer Email: {buyer.email}<br>
            Buyer Phone Number: {buyer.profile.phone_number}<br><br>

            They have been sent an email informing them that you have accepted an offer, and to contact you as soon as possible to arrange pickup.<br><br>

            Best of luck,<br>
            The Sell Your Tackle Team
            """
            text_content_to_seller = strip_tags(html_content_to_seller)  # this strips the html, so people will have the text as well.

            # create the email, and attach the HTML version as well as the text version.
            email_to_seller = EmailMultiAlternatives(subject_to_seller, text_content_to_seller, settings.FROM_EMAIL, [seller.email])
            email_to_seller.attach_alternative(html_content_to_seller, "text/html")
            threading.Thread(target=send_async_email, args=(email_to_seller,)).start()

            
            
            
         