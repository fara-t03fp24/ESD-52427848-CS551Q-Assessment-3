from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address']
        widgets = {
            'shipping_address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Enter the delivery address for your 3D printed items'
                }
            )
        }
        help_texts = {
            'shipping_address': 'Please provide a complete address where you would like to receive your 3D printed items.'
        }

class CartItemForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Number of prints'
            }
        ),
        help_text='Enter the number of copies you want printed'
    )