from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.functions import TruncMonth
from .models import Category, Product, Shop
from apps.orders.models import OrderItem
from .forms import ProductForm, ShopForm
import datetime


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.select_related('category', 'seller', 'shop').prefetch_related('images')
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
        
        # Add current category object to context
        if context['current_category']:
            context['current_category_obj'] = get_object_or_404(
                Category, 
                slug=context['current_category']
            )
            
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
    success_url = reverse_lazy('products:product_list')

    def test_func(self):
        return hasattr(self.request.user, 'shop')

    def handle_no_permission(self):
        messages.error(self.request, 'You need to create a shop before you can add products.')
        return redirect('products:shop_create')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
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


class ShopListView(ListView):
    model = Shop
    template_name = 'products/shop_list.html'
    context_object_name = 'shops'
    paginate_by = 12

    def get_queryset(self):
        queryset = Shop.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        return queryset.annotate(
            product_count=Count('products'),
            total_sales=Count('products__orderitem')
        )


class ShopCreateView(LoginRequiredMixin, CreateView):
    model = Shop
    form_class = ShopForm
    template_name = 'products/shop_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        # Set user as seller when they create their first shop
        if not self.request.user.is_seller:
            self.request.user.is_seller = True
            self.request.user.save()
        messages.success(self.request, 'Your shop has been created successfully!')
        return super().form_valid(form)


class ShopDetailView(DetailView):
    model = Shop
    template_name = 'products/shop_detail.html'
    context_object_name = 'shop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(is_active=True)
        return context


class ShopUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = 'products/shop_form.html'
    
    def test_func(self):
        shop = self.get_object()
        return self.request.user == shop.owner
    
    def form_valid(self, form):
        messages.success(self.request, 'Shop details updated successfully!')
        return super().form_valid(form)


class ShopDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'products/shop_dashboard.html'
    
    def test_func(self):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.request.user == shop.owner
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        
        # Get products with pagination
        page = self.request.GET.get('page', 1)
        stock_filter = self.request.GET.get('stock', 'all')
        products = shop.products.all()
        
        if stock_filter == 'in_stock':
            products = products.filter(stock__gt=0)
        elif stock_filter == 'out_of_stock':
            products = products.filter(stock=0)
            
        paginator = Paginator(products, 10)  # Show 10 products per page
        
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        
        # Calculate statistics
        now = datetime.datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        orders = OrderItem.objects.filter(product__shop=shop)
        monthly_orders = orders.filter(created_at__gte=start_of_month)
        
        context.update({
            'shop': shop,
            'products': products,
            'total_products': shop.products.count(),
            'active_products': shop.products.filter(is_active=True).count(),
            'total_orders': orders.count(),
            'monthly_orders': monthly_orders.count(),
            'total_revenue': orders.aggregate(
                total=Sum('product__price')
            )['total'] or 0,
            'monthly_revenue': monthly_orders.aggregate(
                total=Sum('product__price')
            )['total'] or 0,
            
            # Order statistics
            'delivered_orders': orders.filter(status='delivered').count(),
            'pending_orders': orders.filter(status='pending').count(),
            'cancelled_orders': orders.filter(status='cancelled').count(),
            
            # Revenue chart data
            'monthly_revenue_data': orders.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                revenue=Sum('product__price')
            ).order_by('month')
        })
        
        return context
