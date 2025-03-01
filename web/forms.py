from django import forms
from api.models import Product, ProductVariant, ProductImage, Category,Banner

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
        widgets = {
            'id': forms.HiddenInput(),  # Hide ID field
        }
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_default']
        widgets = {
            'id': forms.HiddenInput(),  # Hide ID field
        }
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active', 'meta_title', 'meta_description']

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter banner title'}),
        }
