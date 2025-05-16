from .models import Category, Wishlist

def categories_processor(request):
    context = {
        'categories': Category.objects.all()
    }
    
    if request.user.is_authenticated:
        context['wishlist_count'] = Wishlist.objects.filter(user=request.user).count()
    
    return context