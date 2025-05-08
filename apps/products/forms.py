from django import forms
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'category', 'description', 'price', 
            'stock', 'print_time_hours', 'material_type',
            'difficulty_level', 'weight_grams', 'dimensions'
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
                'min': '0',
                'placeholder': 'Estimated print duration'
            }),
            'material_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., PLA, ABS, PETG'
            }),
            'difficulty_level': forms.Select(attrs={
                'class': 'form-select',
                'aria-label': 'Select printing difficulty'
            }),
            'weight_grams': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Model weight in grams'
            }),
            'dimensions': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Format: length x width x height in mm'
            })
        }
        help_texts = {
            'name': 'Choose a descriptive name for your 3D model',
            'description': 'Include printing temperature, infill recommendations, and any special requirements',
            'price': 'Set your price per print, including material costs',
            'stock': 'How many times can you print this model?',
            'print_time_hours': 'Average time to complete one print',
            'material_type': 'Recommended printing material',
            'difficulty_level': 'How challenging is it to print this model successfully?',
            'weight_grams': 'Final printed model weight',
            'dimensions': 'Final printed model dimensions'
        }
    
    def save(self, commit=True):
        product = super().save(commit=commit)
        
        if commit and hasattr(self, 'files'):
            # Handle image uploads
            for image_file in self.files.getlist('product_images'):
                ProductImage.objects.create(
                    product=product,
                    image=image_file,
                    is_primary=not product.images.exists()  # First image is primary
                )
            
            # Handle image deletion
            remove_images = self.data.getlist('remove_images')
            if remove_images:
                ProductImage.objects.filter(
                    id__in=remove_images,
                    product=product
                ).delete()
        
        return product