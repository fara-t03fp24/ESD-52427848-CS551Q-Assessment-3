from django.contrib import admin
from apps.shops.models import Shop


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'owner__email', 'description')
    prepopulated_fields = {'slug': ('name',)}