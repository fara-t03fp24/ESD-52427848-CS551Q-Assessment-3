from django.db import models
from django.core.validators import MinValueValidator
from django.urls import reverse
from apps.common.models import BaseModel
from apps.users.models import User


class Category(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self) -> str:
        return str(self.name)


class Shop(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='shops/banners/', blank=True, null=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self) -> str:
        return str(self.name)
    
    def get_absolute_url(self):
        return reverse('products:shop_detail', kwargs={'slug': self.slug})


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
