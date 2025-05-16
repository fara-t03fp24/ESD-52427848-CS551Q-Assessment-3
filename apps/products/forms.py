from django import forms
from django.utils.text import slugify
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):
    shop = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )

    class Meta:
        model = Product
        fields = [
            'shop', 'name', 'category', 'description', 'price', 
            'stock', 'print_time_hours', 'material_type',
            'difficulty_level', 'weight_grams', 'dimensions',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'print_time_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'material_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'weight_grams': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            })
        }
        help_texts = {
            'description': 'Include printing temperature, infill recommendations, and any special requirements',
            'price': 'Include material costs in your price per print',
            'dimensions': 'Format: length x width x height in mm'
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        if user:
            self.fields['shop'].queryset = user.shops.all()

    def save(self, commit=True):
        product = super().save(commit=False)
        if not product.pk:  # New product
            product.seller = self.user
            product.slug = slugify(product.name)
        
        if commit:
            product.save()
            # Handle image uploads
            if hasattr(self, 'files'):
                for image_file in self.files.getlist('product_images'):
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        is_primary=not product.images.exists()
                    )
                
                # Handle image deletion
                remove_images = self.data.getlist('remove_images')
                if remove_images:
                    ProductImage.objects.filter(
                        id__in=remove_images,
                        product=product
                    ).delete()
        
        return product