from django.contrib import admin
from .models import Category, Product, ProductImage, Shop


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'material_type', 'is_active', 'seller')
    list_filter = ('category', 'material_type', 'difficulty_level', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # if creating new object
            obj.seller = request.user
        super().save_model(request, obj, form, change)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'owner__email')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')
