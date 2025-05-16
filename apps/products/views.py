from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Q, Case, When, Exists, OuterRef
from django.contrib import messages
from .models import Product, Category, Wishlist
from .forms import ProductForm
from apps.shops.models import Shop


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        search = self.request.GET.get('q', '').strip()
        category_slug = self.request.GET.get('category')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Add wishlist annotation if user is authenticated
        if self.request.user.is_authenticated:
            queryset = queryset.annotate(
                is_wishlisted=Exists(
                    Wishlist.objects.filter(
                        user=self.request.user,
                        product=OuterRef('pk')
                    )
                )
            )
        
        return queryset.select_related('category', 'shop').prefetch_related('images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('q', '').strip()
        category_slug = self.request.GET.get('category')
        
        context['query'] = search
        context['current_category'] = None
        
        if category_slug:
            context['current_category'] = Category.objects.filter(slug=category_slug).first()

        if search:
            # Get matching shops
            shops = Shop.objects.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search),
                is_active=True
            )[:5]  # Limit to 5 shops

            # Get matching products
            products = self.get_queryset()[:5]  # Limit to 5 products

            # Add search results for the dropdown
            context['search_results'] = {
                'shops': shops,
                'products': products
            }

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


class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product', 'product__shop')


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, f"{product.name} removed from your wishlist")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        messages.success(request, f"{product.name} added to your wishlist")
    
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))
