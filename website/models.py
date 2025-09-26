# website/models.py
from django.db import models
from django.urls import reverse
from django.utils import timezone

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Al-Hadid Foundation")
    tagline = models.CharField(max_length=200, default="Empowering Communities, Building Futures")
    description = models.TextField(default="Al-Hadid Foundation is dedicated to improving lives through education, healthcare, and community development programs.")
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    google_maps_embed = models.TextField(blank=True)

    # NEW: impact numbers (optional; ukiziacha tupu hazitaoneshwa kwenye templates)
    lives_touched = models.PositiveIntegerField(null=True, blank=True)
    regions_served = models.PositiveIntegerField(null=True, blank=True)
    years_of_service = models.PositiveIntegerField(null=True, blank=True)
    founded_year = models.PositiveIntegerField(null=True, blank=True)

    # NEW: About impact blocks
    impact_orphans_supported = models.PositiveIntegerField(null=True, blank=True)
    impact_women_empowered = models.PositiveIntegerField(null=True, blank=True)
    impact_mosques_developed = models.PositiveIntegerField(null=True, blank=True)
    impact_babies_assisted = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name


class Program(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='programs/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class News(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "News"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('website:news_detail', args=[self.pk])


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_date = models.DateTimeField()
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['event_date']

    def __str__(self):
        return self.title

    @property
    def is_upcoming(self):
        return self.event_date > timezone.now()


class DonationMethod(models.Model):
    name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Gallery(models.Model):
    class Category(models.TextChoices):
        ORPHANS = 'orphans', 'Orphans'
        WOMEN = 'women', 'Women'
        MOSQUES = 'mosques', 'Mosques'
        HEALTHCARE = 'healthcare', 'Healthcare'
        EVENTS = 'events', 'Events'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='gallery/')
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER, db_index=True)  # NEW
    is_published = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Gallery"

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # NEW: kwa view yako ya contact
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.subject} - {self.name}"
