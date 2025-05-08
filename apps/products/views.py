from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .models import Category, Product, ProductImage
from .forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'seller').prefetch_related('images')
        q = self.request.GET.get('q')
        category = self.request.GET.get('category')
        sort = self.request.GET.get('sort')

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(description__icontains=q) |
                Q(category__name__icontains=q)
            )
        
        if category:
            queryset = queryset.filter(category__slug=category)
        
        if sort:
            if sort == 'price_low':
                queryset = queryset.order_by('price')
            elif sort == 'price_high':
                queryset = queryset.order_by('-price')
            elif sort == 'newest':
                queryset = queryset.order_by('-created_at')
            
        return queryset.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category')
        context['current_sort'] = self.request.GET.get('sort')
        context['query'] = self.request.GET.get('q')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Product.objects.select_related('category', 'seller').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.object.is_active and self.object.seller != self.request.user:
            messages.error(self.request, "This 3D model is currently unavailable for printing.")
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products:product_list')

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.slug = form.instance.name.lower().replace(' ', '-')
        response = super().form_valid(form)
        messages.success(self.request, 'Your 3D model has been successfully added to the marketplace!')
        return response


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def get_success_url(self):
        messages.success(self.request, '3D model details have been successfully updated!')
        return reverse_lazy('products:product_detail', kwargs={'slug': self.object.slug})


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')
    
    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '3D model has been removed from the marketplace!')
        return super().delete(request, *args, **kwargs)
