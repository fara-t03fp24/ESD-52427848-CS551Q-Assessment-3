from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('<slug:slug>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
    
    # Shop URLs
    path('shops/', views.ShopListView.as_view(), name='shop_list'),
    path('shops/create/', views.ShopCreateView.as_view(), name='shop_create'),
    path('shops/<slug:slug>/', views.ShopDetailView.as_view(), name='shop_detail'),
    path('shops/<slug:slug>/dashboard/', views.ShopDashboardView.as_view(), name='shop_dashboard'),
    path('shops/<slug:slug>/update/', views.ShopUpdateView.as_view(), name='shop_update'),
]