from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver

# App label ya models zako ni 'website'
APP = 'website'

ROLES = {
    # Ana view/add/change/delete kwa Program, News, Event, Gallery, DonationMethod, ContactMessage, na view/change SiteSettings
    "Manager": [
        # Programs
        "view_program","add_program","change_program","delete_program",
        # News
        "view_news","add_news","change_news","delete_news",
        # Events
        "view_event","add_event","change_event","delete_event",
        # Gallery
        "view_gallery","add_gallery","change_gallery","delete_gallery",
        # Donations
        "view_donationmethod","add_donationmethod","change_donationmethod","delete_donationmethod",
        # Messages
        "view_contactmessage","change_contactmessage","delete_contactmessage",
        # Settings
        "view_sitesettings","change_sitesettings",
    ],
    # Editor: view/add/change (no delete) kwenye content, anaweza mark read msgs
    "Editor": [
        "view_program","add_program","change_program",
        "view_news","add_news","change_news",
        "view_event","add_event","change_event",
        "view_gallery","add_gallery","change_gallery",
        "view_donationmethod","add_donationmethod","change_donationmethod",
        "view_contactmessage","change_contactmessage",
        "view_sitesettings",
    ],
    # Viewer: view tu
    "Viewer": [
        "view_program","view_news","view_event","view_gallery",
        "view_donationmethod","view_contactmessage","view_sitesettings",
    ],
    # Comms (habari/matukio tu)
    "Comms": [
        "view_news","add_news","change_news",
        "view_event","add_event","change_event",
    ],
    # Finance (donations tu)
    "Finance": [
        "view_donationmethod","add_donationmethod","change_donationmethod",
    ],
    # Support (kusimamia ujumbe)
    "Support": [
        "view_contactmessage","change_contactmessage","delete_contactmessage",
    ],
}

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # endesha mara baada ya migrations za app yoyote—tutajaribu tu kupata permissions
    for group_name, codenames in ROLES.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        perms = Permission.objects.filter(codename__in=codenames, content_type__app_label=APP)
        group.permissions.set(perms)  # override to keep clean
        group.save()
