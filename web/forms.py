from django import forms
from api.models import Product, ProductVariant, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'is_active', 'is_featured', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'value', 'price', 'stock']

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_default']
