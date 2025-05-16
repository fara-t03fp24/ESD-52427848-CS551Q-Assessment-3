from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
from .models import Product
from .forms import ProductForm
from apps.shops.models import Shop


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        category = self.request.GET.get('category')
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__slug=category)
            
        return queryset.select_related('category', 'seller')


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


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def test_func(self):
        shop = get_object_or_404(Shop, slug=self.kwargs['shop_slug'])
        return self.request.user == shop.owner

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        shop = get_object_or_404(Shop, slug=self.kwargs['shop_slug'])
        form.instance.shop = shop
        form.instance.seller = self.request.user
        messages.success(self.request, 'Your 3D model has been created!')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop'] = get_object_or_404(Shop, slug=self.kwargs['shop_slug'])
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Your 3D model has been updated!')
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products:product_list')

    def get_queryset(self):
        return Product.objects.filter(seller=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Your 3D model has been deleted!')
        return super().delete(request, *args, **kwargs)


@login_required
def toggle_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.user != product.shop.owner:
        messages.error(request, "You don't have permission to modify this product.")
        return redirect('shops:shop_dashboard', slug=product.shop.slug)
        
    product.is_active = not product.is_active
    product.save()
    
    status = "activated" if product.is_active else "deactivated"
    messages.success(request, f'Product {product.name} has been {status}.')
    
    return redirect('shops:shop_dashboard', slug=product.shop.slug)
