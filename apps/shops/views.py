import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum, F
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
import datetime

# Local imports
from .models import Shop
from .forms import ShopForm
from apps.orders.models import OrderItem
from apps.products.models import Product


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
        
        # Get products with search and filtering
        products = shop.products.all()
        
        # Handle search
        search_query = self.request.GET.get('search')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(id__icontains=search_query)
            )
            
        # Handle stock filter
        stock_filter = self.request.GET.get('stock')
        if stock_filter == 'in':
            products = products.filter(stock__gt=0)
        elif stock_filter == 'out':
            products = products.filter(stock=0)
            
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(products, 9)  # Show 9 products per page
        
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        
        context.update({
            'shop': shop,
            'products': products,
        })
        
        return context


class ShopAnalyticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'shops/shop_analytics.html'
    
    def test_func(self):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.request.user == shop.owner
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        
        # Calculate statistics
        now = datetime.datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        orders = OrderItem.objects.filter(product__shop=shop)
        monthly_orders = orders.filter(created_at__gte=start_of_month)
        
        context.update({
            'shop': shop,
            'total_products': shop.products.count(),
            'active_products': shop.products.filter(is_active=True).count(),
            'total_orders': orders.count(),
            'monthly_orders': monthly_orders.count(),
            'total_revenue': orders.aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0,
            'monthly_revenue': monthly_orders.aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0,
            'delivered_orders': orders.filter(order__status='delivered').count(),
            'pending_orders': orders.filter(order__status='pending').count(),
        })
        
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return chart data for AJAX requests
            shop = context['shop']
            
            # Get sales data for the last 30 days
            today = datetime.date.today()
            thirty_days_ago = today - datetime.timedelta(days=30)
            
            daily_sales = OrderItem.objects.filter(
                product__shop=shop,
                created_at__date__gte=thirty_days_ago
            ).values('created_at__date').annotate(
                total=Sum(F('price') * F('quantity'))
            ).order_by('created_at__date')
            
            # Get top products
            top_products = Product.objects.filter(shop=shop).annotate(
                order_count=Count('orderitem')
            ).order_by('-order_count')[:5]
            
            chart_data = {
                'sales': {
                    'labels': [sale['created_at__date'].strftime('%b %d') for sale in daily_sales],
                    'values': [float(sale['total']) for sale in daily_sales]
                },
                'top_products': {
                    'labels': [product.name for product in top_products],
                    'values': [product.order_count for product in top_products]
                }
            }
            
            return JsonResponse(chart_data)
            
        return super().get(request, *args, **kwargs)


class ShopOrdersView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'shops/shop_orders.html'
    
    def test_func(self):
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        return self.request.user == shop.owner
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = get_object_or_404(Shop, slug=self.kwargs['slug'])
        
        # Get orders
        orders = OrderItem.objects.filter(product__shop=shop).select_related(
            'order', 'product', 'order__user'
        ).order_by('-created_at')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status and status != 'all':
            orders = orders.filter(order__status=status)
        
        # Pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(orders, 20)
        
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)
        
        context.update({
            'shop': shop,
            'orders': orders,
        })
        
        return context


class ShopSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Shop
    form_class = ShopForm
    template_name = 'shops/shop_settings.html'
    context_object_name = 'shop'
    
    def test_func(self):
        shop = self.get_object()
        return self.request.user == shop.owner
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shop = self.get_object()
        
        context.update({
            'total_products': shop.products.count(),
            'total_orders': OrderItem.objects.filter(product__shop=shop).count(),
        })
        
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Shop settings updated successfully!')
        return super().form_valid(form)


@login_required
def update_order_status(request, pk):
    order_item = get_object_or_404(OrderItem, pk=pk, product__shop__owner=request.user)
    status = request.POST.get('status')
    
    if status and status in ['processing', 'completed']:
        order_item.order.status = status
        order_item.order.save()
        messages.success(request, f'Order status updated to {status}')
    
    return redirect('shops:shop_orders', slug=order_item.product.shop.slug)


@login_required
def shop_select(request):
    shop_slug = request.GET.get('shop_slug')
    if not shop_slug:
        return redirect('shops:shop_list')
        
    if shop_slug == 'create':
        return redirect('shops:shop_create')
        
    shop = get_object_or_404(Shop, slug=shop_slug, owner=request.user)
    return redirect('shops:shop_dashboard', slug=shop_slug)