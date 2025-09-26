# admin_panel/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'admin_panel'

urlpatterns = [
    # Auth
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard & settings
    path('', views.dashboard, name='dashboard'),
    path('settings/', views.site_settings, name='site_settings'),

    # Programs
    path('programs/', views.programs_list, name='programs_list'),
    path('programs/add/', views.program_add, name='programs_create'),
    path('programs/<int:pk>/edit/', views.program_edit, name='programs_update'),
    path('programs/<int:pk>/delete/', views.program_delete, name='programs_delete'),

    # News
    path('news/', views.news_list, name='news_list'),
    path('news/add/', views.news_add, name='news_create'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_update'),
    path('news/<int:pk>/delete/', views.news_delete, name='news_delete'),

    # Events
    path('events/', views.events_list, name='events_list'),
    path('events/add/', views.events_add, name='events_create'),
    path('events/<int:pk>/edit/', views.events_edit, name='events_update'),
    path('events/<int:pk>/delete/', views.events_delete, name='events_delete'),

    # Gallery
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/add/', views.gallery_add, name='gallery_create'),
    path('gallery/<int:pk>/edit/', views.gallery_edit, name='gallery_update'),
    path('gallery/<int:pk>/delete/', views.gallery_delete, name='gallery_delete'),

    # Donations
    path('donations/', views.donations_list, name='donations_list'),
    path('donations/add/', views.donations_add, name='donations_create'),
    path('donations/<int:pk>/edit/', views.donations_edit, name='donations_update'),
    path('donations/<int:pk>/delete/', views.donations_delete, name='donations_delete'),

    # Messages
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<int:pk>/', views.message_detail, name='message_detail'),
    path('messages/<int:pk>/delete/', views.message_delete, name='message_delete'),
    path('messages/<int:pk>/read/', views.messages_mark_read, name='messages_mark_read'),
    path('messages/<int:pk>/unread/', views.messages_mark_unread, name='messages_mark_unread'),
    path('messages/read-all/', views.messages_mark_all_read, name='messages_mark_all_read'),  # NEW

    # Users & roles
    path('', include('admin_panel.users_urls')),

    # Password reset (unchanged) ...
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='admin_panel/auth/password_reset_form.html',
        email_template_name='admin_panel/auth/password_reset_email.txt',
        subject_template_name='admin_panel/auth/password_reset_subject.txt',
    ), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='admin_panel/auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='admin_panel/auth/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='admin_panel/auth/password_reset_complete.html'
    ), name='password_reset_complete'),
]
