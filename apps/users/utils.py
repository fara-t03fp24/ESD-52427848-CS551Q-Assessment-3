import re
from django.core.exceptions import ValidationError


def validate_password_strength(password):
    """
    Validate password strength.
    Must be at least 8 characters long and contain:
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError('Password must contain at least one uppercase letter.')
    
    if not re.search(r'[a-z]', password):
        raise ValidationError('Password must contain at least one lowercase letter.')
    
    if not re.search(r'[0-9]', password):
        raise ValidationError('Password must contain at least one number.')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError('Password must contain at least one special character.')


def get_user_display_name(user):
    """
    Return a display name for the user.
    If full name is available, return that, otherwise return email.
    """
    if user.get_full_name():
        return user.get_full_name()
    return user.email


def check_user_completion(user):
    """
    Check if user has completed their profile.
    Returns tuple of (is_complete, missing_fields)
    """
    required_fields = ['first_name', 'last_name', 'email']
    missing_fields = []
    
    for field in required_fields:
        if not getattr(user, field):
            missing_fields.append(field.replace('_', ' ').title())
    
    return (len(missing_fields) == 0, missing_fields)


def get_seller_stats(user):
    """
    Get statistics for a seller's shop.
    Returns dict with stats or None if user is not a seller.
    """
    if not user.is_seller or not hasattr(user, 'shop'):
        return None
    
    shop = user.shop
    stats = {
        'total_products': shop.products.count(),
        'active_products': shop.products.filter(is_active=True).count(),
        'total_orders': shop.products.filter(orderitem__isnull=False).distinct().count(),
        'revenue': sum(
            item.price * item.quantity 
            for product in shop.products.all()
            for item in product.orderitem_set.all()
        )
    }
    return stats