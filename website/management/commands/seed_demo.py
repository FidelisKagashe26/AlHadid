from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from website.models import (
    SiteSettings, Program, News, Event, DonationMethod,
    Gallery, ContactMessage
)


class Command(BaseCommand):
    help = "Seed demo content for Al-Hadid Foundation (safe to run multiple times)."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding demo data..."))

        # -----------------------------
        # Site Settings
        # -----------------------------
        settings_defaults = {
            "site_name": "AL-HADID FOUNDATION",
            "tagline": "Empowering Communities Through Charity, Knowledge, and Faith",
            "description": (
                "The Al-Hadid Foundation is a faith-driven, non-profit organization dedicated to "
                "uplifting vulnerable communities and promoting Islamic values of compassion and service. "
                "Founded by Zuberi Daffa, Al-Hadid serves humanity through care, empowerment and development."
            ),
            "phone": "0758150976",
            "email": "info@alhadid.or.tz",
            "address": "Morogoro, Tanzania",
            "facebook_url": "",
            "twitter_url": "",
            "instagram_url": "",
            "whatsapp_number": "0758150976",
            "google_maps_embed": "",
        }
        SiteSettings.objects.update_or_create(pk=1, defaults=settings_defaults)
        self.stdout.write(self.style.SUCCESS("✓ SiteSettings saved/updated"))

        # -----------------------------
        # Programs
        # -----------------------------
        programs = [
            {
                "title": "Orphan Support Program",
                "description": (
                    "Monthly food, clothing, and school materials for orphans, plus mentorship "
                    "and counseling to nurture a brighter Islamic and academic future."
                ),
                "is_active": True,
            },
            {
                "title": "Women’s Islamic Empowerment",
                "description": (
                    "Weekly Islamic study circles and practical vocational training so women can "
                    "thrive spiritually and economically."
                ),
                "is_active": True,
            },
            {
                "title": "Mosque Development Initiative",
                "description": (
                    "Building and renovating mosques in underserved areas to strengthen community ties "
                    "and dignity in worship."
                ),
                "is_active": True,
            },
            {
                "title": "Premature Baby Care Support",
                "description": (
                    "Medical and financial support for premature babies: equipping hospitals and "
                    "assisting needy families with bills."
                ),
                "is_active": True,
            },
        ]
        for p in programs:
            Program.objects.update_or_create(title=p["title"], defaults=p)
        self.stdout.write(self.style.SUCCESS(f"✓ Programs: {Program.objects.count()} total"))

        # -----------------------------
        # News
        # -----------------------------
        news_items = [
            {
                "title": "Al-Hadid Distributes School Kits to Orphans",
                "content": (
                    "Al-Hadid Foundation delivered school bags, uniforms and Qur’an readers to dozens of "
                    "orphans in Morogoro. Baraka to all donors who made this possible."
                ),
                "is_published": True,
            },
            {
                "title": "Women’s Halaqa Expands to New Wards",
                "content": (
                    "Our Women’s Islamic Empowerment circles now run weekly across additional wards. "
                    "Sessions blend Qur’anic lessons and practical livelihood skills."
                ),
                "is_published": True,
            },
        ]
        for n in news_items:
            News.objects.update_or_create(title=n["title"], defaults=n)
        self.stdout.write(self.style.SUCCESS(f"✓ News: {News.objects.count()} total"))

        # -----------------------------
        # Events
        # Your Event model uses `event_date` (DATE field), not `start_datetime`.
        # -----------------------------
        today = timezone.localdate()
        events = [
            {
                "title": "Community Iftar & Fundraiser",
                "description": (
                    "Join us for a community iftar to support orphans and premature baby care."
                ),
                "event_date": today + timedelta(days=14),
                "location": "Masjid Al-Nur, Morogoro",
                "is_published": True,
            },
            {
                "title": "Women’s Halaqa Graduation",
                "description": (
                    "Recognition ceremony for sisters completing the 12-week empowerment program."
                ),
                "event_date": today + timedelta(days=30),
                "location": "Al-Hadid Training Centre, Morogoro",
                "is_published": True,
            },
            {
                "title": "Mosque Renovation Launch",
                "description": (
                    "Kick-off for renovation works in an underserved neighborhood mosque."
                ),
                "event_date": today + timedelta(days=45),
                "location": "Kihonda, Morogoro",
                "is_published": True,
            },
        ]
        for e in events:
            Event.objects.update_or_create(title=e["title"], defaults=e)
        self.stdout.write(self.style.SUCCESS(f"✓ Events: {Event.objects.count()} total"))

        # -----------------------------
        # Gallery
        # (Images left blank to avoid file handling; you can upload via Admin later.)
        # -----------------------------
        gallery_items = [
            {
                "title": "Orphans Receive School Kits",
                "description": "A day of smiles as children receive essentials for the new term.",
                "is_published": True,
            },
            {
                "title": "Sisters in Halaqa",
                "description": "Weekly Islamic study circle and discussion on Seerah.",
                "is_published": True,
            },
            {
                "title": "Mosque Renovation Team",
                "description": "Volunteers surveying a rural masjid ahead of renovations.",
                "is_published": True,
            },
        ]
        for g in gallery_items:
            Gallery.objects.update_or_create(title=g["title"], defaults=g)
        self.stdout.write(self.style.SUCCESS(f"✓ Gallery: {Gallery.objects.count()} total"))

        # -----------------------------
        # Donation Methods
        # Your DonationMethod model fields (per your views): name, account_number, bank_name,
        # description, is_active, order
        # -----------------------------
        donation_methods = [
            {
                "name": "M-Pesa (Zuberi Daffa)",
                "account_number": "0758150976",
                "bank_name": "Vodacom M-Pesa",
                "description": "M-Pesa direct number for contributions and sadaqah.",
                "is_active": True,
                "order": 1,
            },
            {
                "name": "Tigopesa (Zuberi Daffa)",
                "account_number": "0758150976",
                "bank_name": "Tigo Pesa",
                "description": "Alternative mobile money channel.",
                "is_active": True,
                "order": 2,
            },
            {
                "name": "Bank Transfer",
                "account_number": "1627779677",
                "bank_name": "CRDB Bank",
                "description": "Use reference: AL-HADID DONATION",
                "is_active": True,
                "order": 3,
            },
        ]
        for d in donation_methods:
            DonationMethod.objects.update_or_create(
                name=d["name"], defaults=d
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Donation methods: {DonationMethod.objects.count()} total"))

        # -----------------------------
        # Contact Messages (sample)
        # -----------------------------
        messages = [
            {
                "name": "Amina",
                "email": "amina@example.com",
                "subject": "Volunteering",
                "message": "Salaam, I’d love to volunteer in the women’s program. How can I join?",
                "is_read": False,
            },
            {
                "name": "Mohamed",
                "email": "mohamed@example.com",
                "subject": "Donation Receipt",
                "message": "I made an M-Pesa donation. Please share a receipt for my records.",
                "is_read": False,
            },
        ]
        for m in messages:
            ContactMessage.objects.update_or_create(
                email=m["email"], subject=m["subject"], defaults=m
            )
        self.stdout.write(self.style.SUCCESS(f"✓ Contact messages: {ContactMessage.objects.count()} total"))

        # -----------------------------
        # Recap
        # -----------------------------
        recap = (
            f"\nDone!\n"
            f"  Site: {SiteSettings.objects.count()} settings record\n"
            f"  Programs: {Program.objects.count()}\n"
            f"  News: {News.objects.count()}\n"
            f"  Events: {Event.objects.count()}\n"
            f"  Gallery: {Gallery.objects.count()}\n"
            f"  Donations: {DonationMethod.objects.count()}\n"
            f"  Messages: {ContactMessage.objects.count()}\n"
        )
        self.stdout.write(self.style.HTTP_INFO(recap))
