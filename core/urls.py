from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.views.defaults import page_not_found, server_error, permission_denied

# Custom error handlers
handler404 = lambda request, exception: page_not_found(request, exception, template_name='errors/404.html')
handler500 = lambda request: server_error(request, template_name='errors/500.html')
handler403 = lambda request, exception: permission_denied(request, exception, template_name='errors/403.html')

# Authentication URL patterns
auth_patterns = [
    path('login/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='products:product_list'
    ), name='logout'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(pattern_name='products:product_list', permanent=True), name='home'),
    path('products/', include('apps.products.urls')),
    path('orders/', include('apps.orders.urls')),
    path('users/', include('apps.users.urls')),
    path('shops/', include('apps.shops.urls')),
    
    # Authentication URLs
    path('auth/', include((auth_patterns, 'auth'))),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
