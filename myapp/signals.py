from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.conf import settings
import threading
from django.core.mail import EmailMessage

def send_async_email(email_message):
    try:
        email_message.send()
    except Exception as e:
        print(f"Exception occurred: {e}")

@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):
    subject = "Sell Your Tackle Login"
    body = "You have successfully logged in to your Sell Your Tackle account."
    email = EmailMessage(subject, body, settings.FROM_EMAIL, [user.email])
    threading.Thread(target=send_async_email, args=(email,)).start()


