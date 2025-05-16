from django.db import models
from django.core.validators import MinValueValidator
from apps.common.models import BaseModel
from apps.users.models import User
from apps.shops.models import Shop


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self) -> str:
        return str(self.name)


class Product(BaseModel):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    MATERIAL_CHOICES = [
        ('pla', 'PLA'),
        ('abs', 'ABS'),
        ('petg', 'PETG'),
        ('tpu', 'TPU'),
        ('nylon', 'Nylon'),
        ('resin', 'Resin'),
        ('carbon', 'Carbon Fiber'),
        ('metal', 'Metal-Infused'),
        ('wood', 'Wood-Infused'),
        ('other', 'Other'),
    ]
    
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='products', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    print_time_hours = models.PositiveIntegerField(help_text="Estimated printing time in hours")
    material_type = models.CharField(
        max_length=20, 
        choices=MATERIAL_CHOICES,
        default='pla',
        help_text="Select the recommended printing material"
    )
    difficulty_level = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    weight_grams = models.PositiveIntegerField(help_text="Weight in grams")
    dimensions = models.CharField(max_length=50, help_text="Format: length x width x height in mm")
    is_active = models.BooleanField(default=True)
    seller = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return str(self.name)


class ProductImage(BaseModel):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/images/')
    is_primary = models.BooleanField(default=False)
    
    def __str__(self) -> str:
        return f"Image for {str(self.product.name)}"


class Wishlist(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='wishlists')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email}'s wish - {self.product.name}"
