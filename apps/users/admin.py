from django.contrib import admin
from apps.users.models import User


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    search_fields = ('first_name', 'last_name', 'phone')
    ordering = ('id',)


admin.site.register(User, UserAdmin)
