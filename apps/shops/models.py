from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from apps.common.models import BaseModel
from apps.users.models import User


class Shop(BaseModel):
    name = models.CharField(
        max_length=100, 
        unique=True,
        help_text="Shop name (lowercase letters, numbers, hyphens and underscores only)",
        validators=[
            RegexValidator(
                regex='^[a-z0-9-_]+$',
                message='Shop name can only contain lowercase letters, numbers, hyphens and underscores'
            )
        ]
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shops')
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='shops/logos/', blank=True, null=True)
    banner = models.ImageField(upload_to='shops/banners/', blank=True, null=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
    
    def __str__(self) -> str:
        return str(self.name)
    
    def get_absolute_url(self):
        return reverse('shops:shop_detail', kwargs={'slug': self.slug})
    
    def clean(self):
        if self.name:
            # Convert to lowercase
            self.name = self.name.lower()
            # Check for spaces
            if ' ' in self.name:
                raise ValidationError('Shop name cannot contain spaces. Use hyphens or underscores instead.')