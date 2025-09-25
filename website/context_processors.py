from .models import SiteSettings

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
    except:
        settings = None
    
    theme = request.session.get('theme', 'light')
    
    return {
        'site_settings': settings,
        'current_theme': theme,
    }