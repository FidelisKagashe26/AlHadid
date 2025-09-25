from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from website import models as m

def add_perms(group, model, actions=('view',)):
    ct = ContentType.objects.get_for_model(model)
    codes = [f'{a}_{model._meta.model_name}' for a in actions]
    perms = Permission.objects.filter(content_type=ct, codename__in=codes)
    group.permissions.add(*perms)

class Command(BaseCommand):
    help = "Create default roles (groups) and attach permissions"

    def handle(self, *args, **opts):
        roles = {
            # anaweza kusoma kila kitu – read only
            'Reader': [
                (m.Program, ('view',)),
                (m.News, ('view',)),
                (m.Event, ('view',)),
                (m.Gallery, ('view',)),
                (m.DonationMethod, ('view',)),
                (m.ContactMessage, ('view',)),
                (m.SiteSettings, ('view',)),
            ],
            # Content Editor: Programs/News/Events/Gallery add+change (no delete)
            'Content Editor': [
                (m.Program, ('view','add','change')),
                (m.News, ('view','add','change')),
                (m.Event, ('view','add','change')),
                (m.Gallery, ('view','add','change')),
                (m.ContactMessage, ('view',)),  # kuona inbox tu
            ],
            # Events Manager: full control on Events
            'Events Manager': [
                (m.Event, ('view','add','change','delete')),
            ],
            # Finance: donations only
            'Donations Manager': [
                (m.DonationMethod, ('view','add','change','delete')),
            ],
            # Support: soma na mark read/unread (change), no delete
            'Support': [
                (m.ContactMessage, ('view','change')),
            ],
            # Site Manager: settings + everything view
            'Site Manager': [
                (m.SiteSettings, ('view','change')),
                (m.Program, ('view',)),
                (m.News, ('view',)),
                (m.Event, ('view',)),
                (m.Gallery, ('view',)),
                (m.DonationMethod, ('view',)),
                (m.ContactMessage, ('view',)),
            ],
        }

        for name, rules in roles.items():
            group, _ = Group.objects.get_or_create(name=name)
            for model, acts in rules:
                add_perms(group, model, acts)
            self.stdout.write(self.style.SUCCESS(f'✓ {name} updated'))

        self.stdout.write(self.style.SUCCESS('All roles seeded.'))
