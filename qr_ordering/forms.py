from django import forms
from .models import IceCream, Table

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
        fields = ['number']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 bg-background border border-cardBorder rounded-md focus:ring-primary focus:border-primary'}),
        } 