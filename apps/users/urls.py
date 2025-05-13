from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_update, name='profile'),
    path('password/', views.password_change, name='password_change'),
    path('become-seller/', views.become_seller, name='become_seller'),
]

