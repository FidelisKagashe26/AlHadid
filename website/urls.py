# website/urls.py
from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('programs/', views.programs, name='programs'),
    path('donate/', views.donate, name='donate'),
    path('programs/<int:pk>/', views.program_detail, name='program_detail'),
    path('news-events/', views.news_events, name='news_events'),
    path('news/<int:pk>/', views.news_detail, name='news_detail'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('contact/', views.contact, name='contact'),
    path('gallery/', views.gallery_view, name='gallery'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
]
