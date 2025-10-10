from django import forms
from .models import IceCream, Table, Refund

class IceCreamForm(forms.ModelForm):
    class Meta:
        model = IceCream
        fields = ['name', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 bg-background border border-cardBorder rounded-md focus:ring-primary focus:border-primary'}),
            'price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-background border border-cardBorder rounded-md focus:ring-primary focus:border-primary'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full text-textSecondary'}),
        }

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'qr_base_url']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-background border border-cardBorder rounded-md focus:ring-primary focus:border-primary'}),
            'qr_base_url': forms.URLInput(attrs={'class': 'w-full px-4 py-2 bg-background border border-cardBorder rounded-md focus:ring-primary focus:border-primary', 'placeholder': 'https://yourdomain.com'}),
        }

class RefundForm(forms.ModelForm):
    class Meta:
        model = Refund
        fields = ['customer_email', 'customer_name', 'refund_amount']
        widgets = {
            'customer_email': forms.EmailInput(attrs={'class': 'glass-input', 'readonly': True}),
            'customer_name': forms.TextInput(attrs={'class': 'glass-input', 'readonly': True}),
            'refund_amount': forms.NumberInput(attrs={'class': 'glass-input', 'step': '0.01', 'readonly': True}),
        }