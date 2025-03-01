from django.urls import path
from .views import *

urlpatterns = [
   path("add/", add_product, name="add_product"),
   path('products/', product_list, name='product_list'),
   path('product/edit/<int:product_id>/', edit_product, name='edit_product'),
   path("product/delete/<int:product_id>/", delete_product, name="delete_product"),
   path("product/delete/ajax/<int:product_id>/", delete_product_ajax, name="delete_product_ajax"),
   
   path('categories/', category_list, name='category_list'),
   path('categories/add/', category_create, name='category_create'),
   path('categories/edit/<int:pk>/', category_edit, name='category_edit'),
   path('categories/delete/<int:pk>/', category_delete, name='category_delete'),

   path('admin-a/login/', admin_login, name='admin_login'),
   path('admin-a/logout/', admin_logout, name='admin_logout'),
   path('admin-a/dashboard/', admin_dashboard, name='admin_a_dashboard'),\
   
   path('orders/', order_list, name='order_list'),
   path('orders/<int:order_id>/', order_detail, name='order_detail'),
   path('orders/<int:order_id>/update-items/', update_order_items, name='update_order_items'),
   path('product/<slug:slug>/', product_detail, name='product_detail'),

   path("add-banner/", add_banner, name="add_banner"),


]
