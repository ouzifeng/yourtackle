# sitemaps.py
from django.contrib import sitemaps
from django.urls import reverse
from .models import Product 

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['index', 'about', 'contact', 'faq', 'form_view', 'login', 'pricing', 'register']  # update this list with your static view names

    def location(self, item):
        return reverse(item)


sitemaps = {
    'static': StaticViewSitemap,
}
