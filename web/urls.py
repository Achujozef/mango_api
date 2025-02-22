from django.urls import path
from .views import add_product,product_list,edit_product

urlpatterns = [
   path("add/", add_product, name="add_product"),
   path('products/', product_list, name='product_list'),
   path('product/edit/<int:product_id>/', edit_product, name='edit_product'),

]
