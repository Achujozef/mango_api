from django.contrib import admin
from django.urls import path
from .views import *
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('category/add/', CategoryCreateView.as_view(), name='category-add'),
    path('product/add/', ProductCreateView.as_view(), name='product-add'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('cart/recommendations/', CartProductRecommendationView.as_view(), name='cart-recommendations'),
    path('order/recommendations/', PreviousOrderProductRecommendationView.as_view(), name='order-recommendations'),
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', CartListView.as_view(), name='cart-list'),
    path('cart/update/<int:cart_id>/', UpdateCartItemView.as_view(), name='update-cart-item'),
    path('cart/checkout/', CheckoutSummaryView.as_view(), name='checkout-summary'),
    path('cart/checkout/order/', CreateOrderView.as_view(), name='create-order'),
    path('category/<slug:category_slug>/', ProductCategoryView.as_view(), name='category-products'),


]