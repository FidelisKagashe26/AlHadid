from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Keep Django admin available for debugging/backup
    path('django-admin/', admin.site.urls),

    # Public site
    path('', include('website.urls')),

    # Custom admin panel
    path('admin/', include(('admin_panel.urls', 'admin_panel'), namespace='admin_panel')),

    # Users & Roles routes (separate module)
    path('admin/', include('admin_panel.users_urls')),

    # Password reset flow (custom templates under admin_panel)
    path('admin/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='admin_panel/auth/password_reset_form.html',
             email_template_name='admin_panel/auth/password_reset_email.html',
             subject_template_name='admin_panel/auth/password_reset_subject.txt',
             success_url='/admin/password_reset/done/'
         ),
         name='password_reset'),

    path('admin/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='admin_panel/auth/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('admin/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='admin_panel/auth/password_reset_confirm.html',
             success_url='/admin/reset/done/'
         ),
         name='password_reset_confirm'),

    path('admin/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='admin_panel/auth/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

# Optional: sitemap wiring if present in project
try:
    from django.contrib.sitemaps.views import sitemap
    from website.sitemaps import StaticViewSitemap, NewsSitemap, ProgramSitemap
    sitemaps = {
        'static': StaticViewSitemap,
        'news': NewsSitemap,
        'programs': ProgramSitemap,
    }
    urlpatterns.append(path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'))
except Exception:
    pass

# Static & media in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
