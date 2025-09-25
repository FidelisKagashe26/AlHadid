from django.urls import path
from . import views_users

# These routes will be included inside the admin_panel namespace by admin_panel/urls.py
urlpatterns = [
    # Users & Roles
    path('users/', views_users.users_list, name='admin_users_list'),
    path('users/add/', views_users.users_create, name='admin_users_create'),
    path('users/<int:pk>/edit/', views_users.users_update, name='admin_users_update'),
    path('users/<int:pk>/delete/', views_users.users_delete, name='admin_users_delete'),
    path('users/<int:pk>/password/', views_users.users_set_password, name='admin_users_set_password'),

    # Self password change
    path('password/change/', views_users.password_change, name='admin_password_change'),
]
