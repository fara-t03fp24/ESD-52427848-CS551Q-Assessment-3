from django import forms
from django.utils.text import slugify
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):
    shop = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'aria-label': 'Select shop'
        }),
        help_text='Choose which shop this model belongs to'
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
                'class': 'form-control',
                'placeholder': 'Enter the name of your 3D model'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Select model category'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your 3D model, including any special printing instructions or recommendations'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': 'Price per print'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Number of prints available'
            }),
            'print_time_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Estimated print time in hours'
            }),
            'material_type': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Select printing material'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Select difficulty level'
            }),
            'weight_grams': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Weight in grams'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Format: length x width x height in mm'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'role': 'switch'
            })
        }
        help_texts = {
            'name': 'Choose a descriptive name for your 3D model',
            'description': 'Include printing temperature, infill recommendations, and any special requirements',
            'price': 'Set your price per print, including material costs',
            'stock': 'How many times can you print this model?',
            'print_time_hours': 'Average time to complete one print',
            'material_type': 'Choose the recommended material for printing this model',
            'difficulty_level': 'How challenging is it to print this model successfully?',
            'weight_grams': 'Final printed model weight',
            'dimensions': 'Final printed model dimensions',
            'is_active': 'Uncheck to hide this model from your shop',
            'shop': 'Choose which shop this model belongs to'
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