from .models import SiteSettings, Gallery

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        photos_count = Gallery.objects.filter(is_published=True).count()
        if not settings:
            settings = SiteSettings.objects.create()
    except:
        settings = None
    
    theme = request.session.get('theme', 'light')
    
    return {
        'site_settings': settings,
        'current_theme': theme,
        'photos_count': photos_count,
    }