from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from api.models import Product, ProductVariant, Category, ProductImage, Product
from .forms import ProductForm, ProductVariantForm,ProductImageForm
from django.forms import modelformset_factory
from django.core.paginator import Paginator

def product_list(request):
    search_query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=search_query)
    
    paginator = Paginator(products, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/product_list.html', {'page_obj': page_obj, 'search_query': search_query})


def add_product(request):
    ProductVariantFormSet = modelformset_factory(ProductVariant, form=ProductVariantForm, extra=1)
    ProductImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=1)

    if request.method == "POST":
        product_form = ProductForm(request.POST)
        variant_formset = ProductVariantFormSet(request.POST, prefix="variants")
        image_formset = ProductImageFormSet(request.POST, request.FILES, prefix="images")

        if product_form.is_valid():
            product = product_form.save()
            valid_variants = []
            valid_images = []

            if variant_formset.is_valid():
                for variant_form in variant_formset:
                    if variant_form.cleaned_data and not variant_form.cleaned_data.get('DELETE', False):
                        variant = variant_form.save(commit=False)
                        variant.product = product
                        variant.save()
                        valid_variants.append(variant)
            
            if image_formset.is_valid():
                for image_form in image_formset:
                    if image_form.cleaned_data and not image_form.cleaned_data.get('DELETE', False):
                        image = image_form.save(commit=False)
                        image.product = product
                        image.save()
                        valid_images.append(image)

            if not valid_variants:
                product.delete()  # Prevent saving a product without variants
                messages.error(request, "At least one variant is required!")
                return render(request, "products/add_product.html", {
                    "product_form": product_form,
                    "variant_formset": variant_formset,
                    "image_formset": image_formset,
                })

            messages.success(request, "Product added successfully!")
            return redirect('add_product')

        else:
            messages.error(request, "Error in product form. Please correct the errors.")

    else:
        product_form = ProductForm()
        variant_formset = ProductVariantFormSet(queryset=ProductVariant.objects.none(), prefix="variants")
        image_formset = ProductImageFormSet(queryset=ProductImage.objects.none(), prefix="images")

    return render(request, "products/add_product.html", {
        "product_form": product_form,
        "variant_formset": variant_formset,
        "image_formset": image_formset,
    })

from django.forms import modelformset_factory

VariantFormSet = modelformset_factory(ProductVariant, form=ProductVariantForm, extra=0, can_delete=True)
ImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=0, can_delete=True)

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        variant_formset = VariantFormSet(request.POST, queryset=ProductVariant.objects.filter(product=product))
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.filter(product=product))

        if product_form.is_valid() and variant_formset.is_valid() and image_formset.is_valid():
            product_form.save()
            variant_formset.save()
            image_formset.save()
            messages.success(request, "Product updated successfully!")
            return redirect("product_list")
    else:
        product_form = ProductForm(instance=product)
        variant_formset = VariantFormSet(queryset=ProductVariant.objects.filter(product=product))
        image_formset = ImageFormSet(queryset=ProductImage.objects.filter(product=product))

    return render(request, "products/edit_product.html", {
        "product_form": product_form,
        "variant_formset": variant_formset,
        "image_formset": image_formset,
        "product": product
    })