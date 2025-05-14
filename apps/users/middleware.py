from django.utils import timezone
from django.contrib import messages
from .utils import check_user_completion


class UserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Update last activity timestamp
            request.user.last_activity = timezone.now()
            request.user.save(update_fields=['last_activity'])

            # Check profile completion
            is_complete, missing_fields = check_user_completion(request.user)
            if not is_complete and not request.path.startswith('/users/profile'):
                messages.warning(
                    request,
                    f'Please complete your profile to get the most out of PrintCraft. '
                    f'Missing: {", ".join(missing_fields)}.'
                )

            # Seller shop reminder
            if request.user.is_seller and not hasattr(request.user, 'shop'):
                messages.info(
                    request,
                    'You\'re registered as a seller but haven\'t created your shop yet. '
                    '<a href="/products/shops/create/" class="alert-link">Create your shop now</a>!'
                )

        response = self.get_response(request)
        return response