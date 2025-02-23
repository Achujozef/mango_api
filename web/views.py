from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import messages
from api.models import Product, ProductVariant, Category, ProductImage, Product, Customer, Order
from .forms import ProductForm, ProductVariantForm,ProductImageForm,CategoryForm
from django.forms import modelformset_factory
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Sum, Count
from django.http import JsonResponse

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

def category_list(request):
    categories = Category.objects.all()
    paginator = Paginator(categories, 30)  # Show 30 categories per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'categories/category_list.html', {'page_obj': page_obj})

def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully!")
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'categories/category_form.html', {'form': form})

def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully!")
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'categories/category_form.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect('category_list')

def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('admin_a_dashboard')  # Redirect to admin dashboard if already logged in

    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        password = request.POST.get("password")
        user = authenticate(request, phone_number=phone_number, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('admin_a_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin user.")
    
    return render(request, "admin_login.html")

def admin_logout(request):
    """Logs out the admin user and redirects to the login page."""
    if request.method in ['GET', 'POST']:  # Allow both GET and POST
        logout(request)
        messages.success(request, "Logged out successfully!")
        return redirect(reverse('admin_login'))

def admin_dashboard(request):
    print("Called the dashboar view")
    today = now().date()

    # Get total number of customers
    total_customers = Customer.objects.count()

    # Get total orders of today
    total_orders_today = Order.objects.filter(created_at__date=today).count()

    # Get total sale amount of today
    total_sales_today = Order.objects.filter(created_at__date=today).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Monthly sales data
    sales_data = (
        Order.objects.filter(created_at__year=today.year)
        .values('created_at__month')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('created_at__month')
    )

    # Prepare data for the graph
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_sales = [0] * 12
    for entry in sales_data:
        monthly_sales[entry['created_at__month'] - 1] = float(entry['total_sales'])  # Convert Decimal to float

    context = {
        'total_customers': total_customers,
        'total_orders_today': total_orders_today,
        'total_sales_today': total_sales_today,
        'months': months,
        'monthly_sales': monthly_sales,
    }

    return render(request, 'dashboard.html', context)

# 1. List Orders
def order_list(request):
    orders = Order.objects.order_by('-created_at')
    return render(request, 'order/order_list.html', {'orders': orders})

# 2. View Order Details
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.is_viewed = True  # Mark as viewed
    order.save()

    order_items = order.items.all()
    return render(request, 'order/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

# 3. Update Order Items via AJAX
def update_order_items(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        item_ids = request.POST.getlist('selected_items[]')

        # Update able_to_deliver for order items
        for item in order.items.all():
            item.able_to_deliver = str(item.id) in item_ids
            item.save()

        # Recalculate total price
        total_price = order.items.filter(able_to_deliver=True).aggregate(Sum('total_price'))['total_price__sum'] or 0
        order.total_amount = total_price
        order.save()

        return JsonResponse({'success': True, 'total_amount': total_price})
    return JsonResponse({'success': False}, status=400)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    variants = product.variants.all()  # Get all variants related to the product
    return render(request, 'products/product_detail.html', {'product': product, 'variants': variants})

def delete_product(request, product_id, soft_delete=True):
    """Delete a product: Soft delete by default (set is_active=False), or hard delete if requested."""
    product = get_object_or_404(Product, id=product_id)

    if soft_delete:
        product.is_active = False
        product.save()
        messages.success(request, f"Product '{product.name}' has been deactivated (soft deleted).")
    else:
        product.delete()
        messages.success(request, f"Product '{product.name}' has been permanently deleted.")

    return redirect("product_list")  # Change 'product_list' to your actual product listing view name

def delete_product_ajax(request, product_id):
    """AJAX-based deletion request for soft delete (default) or hard delete."""
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        soft_delete = request.POST.get("soft_delete", "true") == "true"

        if soft_delete:
            product.is_active = False
            product.save()
            return JsonResponse({"message": f"Product '{product.name}' has been soft deleted.", "status": "success"})
        else:
            product.delete()
            return JsonResponse({"message": f"Product '{product.name}' has been permanently deleted.", "status": "success"})
    
    return JsonResponse({"message": "Invalid request", "status": "error"}, status=400)