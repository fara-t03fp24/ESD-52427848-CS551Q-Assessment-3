from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.ShopListView.as_view(), name='shop_list'),
    path('create/', views.ShopCreateView.as_view(), name='shop_create'),
    path('select/', views.shop_select, name='shop_select'),
    
    # Shop Dashboard URLs
    path('<slug:slug>/', views.ShopDetailView.as_view(), name='shop_detail'),
    path('<slug:slug>/dashboard/', views.ShopDashboardView.as_view(), name='shop_dashboard'),
    path('<slug:slug>/analytics/', views.ShopAnalyticsView.as_view(), name='shop_analytics'),
    path('<slug:slug>/orders/', views.ShopOrdersView.as_view(), name='shop_orders'),
    path('<slug:slug>/settings/', views.ShopSettingsView.as_view(), name='shop_settings'),
    path('<slug:slug>/edit/', views.ShopUpdateView.as_view(), name='shop_update'),
    path('<slug:slug>/delete/', views.ShopUpdateView.as_view(), name='shop_delete'),
    
    # AJAX endpoints
    path('orders/<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
]