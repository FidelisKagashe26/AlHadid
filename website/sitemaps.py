from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import News, Program

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['website:home', 'website:about', 'website:programs', 
                'website:news_events', 'website:donate', 'website:contact']

    def location(self, item):
        return reverse(item)

class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return News.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class ProgramSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Program.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at