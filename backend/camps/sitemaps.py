from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import SurfCamp, Country


class StaticViewSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return ['/', '/camps', '/map', '/spots']

    def location(self, item):
        return item


class SurfCampSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return SurfCamp.objects.filter(is_active=True)

    def location(self, obj):
        return f'/camps/{obj.slug}'

    def lastmod(self, obj):
        return obj.updated_at


class CountrySitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Country.objects.filter(is_active=True)

    def location(self, obj):
        # Country.slug is added in FIX 7; fall back to code if not set.
        slug = getattr(obj, 'slug', None) or obj.code.lower()
        return f'/{slug}'
