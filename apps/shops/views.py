from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q, Count, Sum
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import datetime

from apps.shops.models import Shop
from apps.shops.forms import ShopForm
from apps.orders.models import OrderItem


class ShopListView(ListView):
    model = Shop
    template_name = 'shops/shop_list.html'
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
    template_name = 'shops/shop_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Your shop has been created successfully!')
        return super().form_valid(form)


class ShopDetailView(DetailView):
    model = Shop
    template_name = 'shops/shop_detail.html'
    context_object_name = 'shop'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.filter(is_active=True)
        return context


class ShopUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = 'shops/shop_form.html'
    
    def test_func(self):
        shop = self.get_object()
        return self.request.user == shop.owner
    
    def form_valid(self, form):
        messages.success(self.request, 'Shop details updated successfully!')
        return super().form_valid(form)


class ShopDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'shops/shop_dashboard.html'
    
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
        })
        return context