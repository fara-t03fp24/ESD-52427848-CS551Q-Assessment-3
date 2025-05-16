from django.urls import path
from . import views

app_name = 'shops'

urlpatterns = [
    path('', views.ShopListView.as_view(), name='shop_list'),
    path('create/', views.ShopCreateView.as_view(), name='shop_create'),
    path('select/', views.shop_select, name='shop_select'),  # New URL pattern for shop selection
    path('<slug:slug>/', views.ShopDetailView.as_view(), name='shop_detail'),
    path('<slug:slug>/dashboard/', views.ShopDashboardView.as_view(), name='shop_dashboard'),
    path('<slug:slug>/update/', views.ShopUpdateView.as_view(), name='shop_update'),
]