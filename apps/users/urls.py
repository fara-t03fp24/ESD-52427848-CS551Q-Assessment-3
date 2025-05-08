from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile_update, name='profile'),
    path('profile/password/', views.password_change, name='password_change'),
]

