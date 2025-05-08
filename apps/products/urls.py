from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('product/<slug:slug>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('product/<slug:slug>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),
]