from .utils import get_seller_stats, get_user_display_name


def user_data(request):
    """
    Add user-related data to the template context
    """
    context = {
        'user_display_name': None,
        'seller_stats': None
    }
    
    if request.user.is_authenticated:
        context['user_display_name'] = get_user_display_name(request.user)
        if request.user.is_seller:
            context['seller_stats'] = get_seller_stats(request.user)
    
    return context