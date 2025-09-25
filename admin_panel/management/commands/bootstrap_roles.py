from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from website import models as wmodels

ROLE_PERMS = {
    'Super Admin': 'ALL',
    'Content Manager': [
        (wmodels.Program, ['add', 'change', 'delete', 'view']),
        (wmodels.News, ['add', 'change', 'delete', 'view']),
        (wmodels.Event, ['add', 'change', 'delete', 'view']),
        (wmodels.Gallery, ['add', 'change', 'delete', 'view']),
    ],
    'Finance (Donate Methods)': [
        (wmodels.DonationMethod, ['add', 'change', 'delete', 'view'])
    ],
    'Site Manager': [
        (wmodels.SiteSettings, ['change', 'view'])
    ],
    'Support (Inbox)': [
        (wmodels.ContactMessage, ['view', 'change'])
    ],
}

class Command(BaseCommand):
    help = 'Create default groups/roles with permissions.'

    def handle(self, *args, **kwargs):
        for role, spec in ROLE_PERMS.items():
            group, _ = Group.objects.get_or_create(name=role)
            if spec == 'ALL':
                group.permissions.set(Permission.objects.all())
                self.stdout.write(self.style.SUCCESS(f"{role}: granted ALL perms"))
                continue
            perms = []
            for model_cls, actions in spec:
                ct = ContentType.objects.get_for_model(model_cls)
                for act in actions:
                    codename = f"{act}_{model_cls._meta.model_name}"
                    try:
                        p = Permission.objects.get(content_type=ct, codename=codename)
                        perms.append(p)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f"Missing perm: {codename}"))
            group.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS(f"{role}: {len(perms)} perms set"))
