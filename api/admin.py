from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import (
    Customer,
    Category,
    Product,
    ProductVariant,
    ProductImage,
    Cart,
    Order,
    OrderItem,
    Coupon,
    Advertisement,
    ProductReview,
    VendorReview,
    SalesReport,
    CustomerActivity,
)
admin.site.register(ProductImage)
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'email', 'first_name', 'last_name', 'created_at')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    list_filter = ( 'created_at',)


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'slug', 'category__name')
    list_filter = ('is_active', 'is_featured', 'category')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'value', 'price', 'stock', 'expiry_date')
    search_fields = ('product__name', 'name', 'value')
    list_filter = ('expiry_date',)


# @admin.register(VariantImage)
# class ProductImageAdmin(admin.ModelAdmin):
#     list_display = ('variant', 'is_default')
#     search_fields = ('variant__name',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_variant', 'quantity', 'added_at')
    search_fields = ('user__username', 'product_variant__product__name')
    list_filter = ('added_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'status', 'payment_method')
    list_filter = ('status', 'payment_method', 'created_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_variant', 'quantity', 'price_per_item', 'total_price')
    search_fields = ('order__order_number', 'product_variant__product__name')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percentage', 'max_discount', 'min_order_amount', 'valid_from', 'valid_until', 'is_active')
    search_fields = ('code',)
    list_filter = ('is_active', 'valid_from', 'valid_until')


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'display_order')
    search_fields = ('title',)
    list_filter = ('is_active',)


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('rating', 'created_at')


@admin.register(VendorReview)
class VendorReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'supplier', 'rating', 'created_at')
    search_fields = ('user__username', 'supplier__username')
    list_filter = ('rating', 'created_at')


@admin.register(SalesReport)
class SalesReportAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_orders')
    search_fields = ('top_products__name',)
    list_filter = ('date',)


@admin.register(CustomerActivity)
class CustomerActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'activity_type', 'timestamp')
    search_fields = ('user__username', 'activity_type')
    list_filter = ('activity_type', 'timestamp')
