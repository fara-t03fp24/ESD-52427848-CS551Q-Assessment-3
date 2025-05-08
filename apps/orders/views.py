from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.urls import reverse
from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm, CartItemForm
from apps.products.models import Product


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'orders/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if quantity > product.stock:
                messages.error(request, f'Sorry, only {product.stock} prints available for this 3D model.')
                return redirect('products:product_detail', slug=product.slug)
            
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                if cart_item.quantity > product.stock:
                    messages.error(request, f'Sorry, only {product.stock} prints available for this 3D model.')
                    return redirect('products:product_detail', slug=product.slug)
                cart_item.save()
            
            messages.success(request, '3D model added to your print queue!')
            return redirect('orders:cart')
    
    return redirect('products:product_list')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, '3D model removed from your print queue!')
    return redirect('orders:cart')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            
            if quantity > cart_item.product.stock:
                messages.error(request, f'Sorry, only {cart_item.product.stock} prints available for this 3D model.')
            elif quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Print queue updated successfully!')
            else:
                cart_item.delete()
                messages.success(request, '3D model removed from your print queue!')
    
    return redirect('orders:cart')


@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    
    if not cart.items.exists():
        messages.error(request, 'Your print queue is empty!')
        return redirect('orders:cart')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total_amount = cart.total_price
            order.save()
            
            # Create order items
            for cart_item in cart.items.all():
                if cart_item.quantity > cart_item.product.stock:
                    messages.error(
                        request,
                        f'Sorry, only {cart_item.product.stock} prints available for {cart_item.product.name}.'
                    )
                    order.delete()
                    return redirect('orders:cart')
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # Clear cart
            cart.items.all().delete()
            
            total_print_time = cart.total_print_time_hours
            messages.success(request, f'Your 3D printing order has been placed! Estimated total print time: {total_print_time} hours.')
            return redirect('orders:order_detail', pk=order.pk)
    else:
        form = CheckoutForm()
    
    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart
    })


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if order.status == 'pending':
        # Restore product stock
        for item in order.items.all():
            product = item.product
            product.stock += item.quantity
            product.save()
        
        order.status = 'cancelled'
        order.save()
        messages.success(request, 'Your 3D printing order has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled as the printing process has already begun!')
    
    return redirect('orders:order_detail', pk=order.pk)
