from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

User = get_user_model()

# Define a custom User Manager
class CustomerManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        phone_number = self.normalize_email(phone_number)
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, password, **extra_fields)

# Define the Customer model
class Customer(AbstractBaseUser):
    phone_number = models.CharField(unique=True, max_length=15, verbose_name="Phone Number")
    email = models.EmailField(unique=True, max_length=255, blank=True, null=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="First Name")
    last_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Last Name")


    # Required fields for AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=now, editable=False, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    objects = CustomerManager()

    USERNAME_FIELD = 'phone_number'  # Using phone_number as the unique identifier
    REQUIRED_FIELDS = []  # No additional required fields for registration

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"

    def __str__(self):
        return f"{self.phone_number} ({self.email if self.email else 'No Email'})"

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True

class Address(BaseModel):
    customer = models.ForeignKey(Customer, related_name='addresses', on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="City")
    state = models.CharField(max_length=100, blank=True, null=True, verbose_name="State")
    pincode = models.CharField(max_length=10, blank=True, null=True, verbose_name="Pincode")
    landmark = models.CharField(max_length=255, blank=True, null=True, verbose_name="Landmark")
    latitude = models.FloatField(blank=True, null=True, verbose_name="Latitude")
    longitude = models.FloatField(blank=True, null=True, verbose_name="Longitude")
    created_at = models.DateTimeField(default=now, editable=False, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.customer.phone_number} - {self.city}, {self.state}"







class Category(MPTTModel):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(BaseModel):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    tags = models.CharField(max_length=255, blank=True, null=True)  

    def __str__(self):
        return self.name


class ProductVariant(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=255)  # e.g., 'Size' or 'Weight'
    value = models.CharField(max_length=255)  # e.g., '1 KG', '500 GM', etc.
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price specific to this variant
    stock = models.PositiveIntegerField()  # Stock specific to this variant
    expiry_date = models.DateField(blank=True, null=True)  # For perishable products

    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value} (₹{self.price})"

    def is_in_stock(self):
        return self.stock > 0

class VariantImage(BaseModel):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='variant_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)  # Optional alt text for the image
    is_default = models.BooleanField(default=False)  # Mark a primary image for the variant

    def __str__(self):
        return f"Image for {self.variant.name} - {self.variant.value}"
    

class Cart(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart", verbose_name="User")
    product_variant = models.ForeignKey(
        'ProductVariant', on_delete=models.CASCADE, related_name="cart_items", verbose_name="Product Variant"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    added_at = models.DateTimeField(default=now, verbose_name="Added At")

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart for {self.user} - {self.product_variant} x {self.quantity}"
    

class Order(BaseModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders", verbose_name="User")
    order_number = models.CharField(max_length=100, unique=True, verbose_name="Order Number")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Amount")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="Order Status")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, verbose_name="Payment Method")
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Delivery Address")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Order Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Order Updated At")

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f"Order {self.order_number} by {self.user}"
    
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="Order")
    product_variant = models.ForeignKey(
        'ProductVariant', on_delete=models.CASCADE, related_name="order_items", verbose_name="Product Variant"
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    price_per_item = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price Per Item")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Price")

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"Item {self.product_variant} in Order {self.order.order_number}"
    

class Coupon(BaseModel):
    code = models.CharField(max_length=20, unique=True, verbose_name="Coupon Code")
    discount_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name="Discount Percentage"
    )
    max_discount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Maximum Discount"
    )
    min_order_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Minimum Order Amount"
    )
    valid_from = models.DateTimeField(verbose_name="Valid From")
    valid_until = models.DateTimeField(verbose_name="Valid Until")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

    def __str__(self):
        return f"Coupon {self.code} - {self.discount_percentage}%"

    def is_valid(self):
        now_date = now()
        return self.is_active and self.valid_from <= now_date <= self.valid_until
    

class Advertisement(BaseModel):
    title = models.CharField(max_length=255, verbose_name="Advertisement Title")
    image = models.ImageField(upload_to='advertisements/', verbose_name="Advertisement Image")
    redirect_url = models.URLField(verbose_name="Redirect URL")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    display_order = models.PositiveIntegerField(
        default=0, verbose_name="Display Order"
    )  # Lower numbers are displayed first.

    class Meta:
        verbose_name = "Advertisement"
        verbose_name_plural = "Advertisements"
        ordering = ['display_order']

    def __str__(self):
        return f"Advertisement {self.title}"
    

class ProductReview(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="product_reviews", verbose_name="User")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Product")
    rating = models.PositiveIntegerField(verbose_name="Rating", choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True, verbose_name="Review Comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return f"Review by {self.user} for {self.product} - {self.rating} Stars"


class VendorReview(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vendor_reviews", verbose_name="User")
    supplier = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_reviews", verbose_name="Supplier")
    rating = models.PositiveIntegerField(verbose_name="Rating", choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True, verbose_name="Review Comment")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Vendor Review"
        verbose_name_plural = "Vendor Reviews"

    def __str__(self):
        return f"Review by {self.user} for Supplier {self.supplier} - {self.rating} Stars"


class SalesReport(BaseModel):
    date = models.DateField(verbose_name="Report Date")
    total_sales = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Total Sales")
    total_orders = models.PositiveIntegerField(verbose_name="Total Orders")
    top_products = models.ManyToManyField(Product, related_name="sales_reports", verbose_name="Top Products")

    class Meta:
        verbose_name = "Sales Report"
        verbose_name_plural = "Sales Reports"

    def __str__(self):
        return f"Sales Report - {self.date}"


class CustomerActivity(BaseModel):
    ACTIVITY_TYPES = [
        ('Login', 'Login'),
        ('Search', 'Search'),
        ('Purchase', 'Purchase'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities", verbose_name="User")
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name="Activity Type")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Timestamp")

    class Meta:
        verbose_name = "Customer Activity"
        verbose_name_plural = "Customer Activities"

    def __str__(self):
        return f"{self.user} - {self.activity_type} at {self.timestamp}"