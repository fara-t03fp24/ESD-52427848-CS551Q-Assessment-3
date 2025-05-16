from django import forms
from django.utils.text import slugify
from .models import Shop


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'description', 'logo', 'banner']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your shop name (lowercase, no spaces)',
                'pattern': '[a-z0-9-_]+',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your shop and what you create'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'banner': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }
        help_texts = {
            'name': 'Shop name can only contain lowercase letters, numbers, hyphens and underscores',
            'description': 'Tell customers about your shop and what kind of 3D models you create',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').lower()
        if ' ' in name:
            raise forms.ValidationError('Shop name cannot contain spaces. Use hyphens or underscores instead.')
        if not name.isascii():
            raise forms.ValidationError('Shop name can only contain ASCII characters.')
        return name

    def save(self, commit=True):
        shop = super().save(commit=False)
        shop.slug = slugify(shop.name)
        if commit:
            shop.save()
        return shop