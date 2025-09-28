from django.core.exceptions import FieldDoesNotExist
from .models import SiteSettings, Gallery

def site_settings(request):
    # Hakikisha tuna rekodi 1 ya settings kila wakati
    settings, _ = SiteSettings.objects.get_or_create(pk=1)

    # Hesabu picha kwa uangalifu (ikiwa model haina is_published, tumia zote)
    try:
        has_is_published = any(f.name == "is_published" for f in Gallery._meta.get_fields())
        photos_qs = Gallery.objects.all()
        if has_is_published:
            photos_qs = photos_qs.filter(is_published=True)
        photos_count = photos_qs.count()
    except Exception:
        photos_count = 0  # fallback salama

    # Theme kutoka kwenye session
    theme = request.session.get("theme", "light")

    return {
        "site_settings": settings,
        "current_theme": theme,
        "photos_count": photos_count,
    }
