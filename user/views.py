from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from api.models import Banner,Category,Product


def index_view(request):
    # Get the latest 5 banners
    banners = Banner.objects.filter(is_deleted=False).order_by('-created_at')[:5]

    # Get all categories
    categories = Category.objects.filter(is_active=True)

    # Get 8 featured products
    featured_products = Product.objects.filter(is_active=True, is_featured=True).order_by('-created_at')[:8]

    # Get the latest 8 added products
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    return render(request, "user/index.html", {
        "banners": banners,
        "categories": categories,
        "featured_products": featured_products,
        "latest_products": latest_products
    })