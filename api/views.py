from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from django.contrib.auth import authenticate
from .models import OTP,Customer,Product,Category,Cart,ProductVariant,OrderItem,Order,ProductReview
from .utils import send_otp
from .helper import generate_otp
from .serializers import CategorySerializer, ProductSerializer,CartSerializer,ProductReviewSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound
from django.db.models import Min
import uuid
from django.db import transaction

User = get_user_model()

class ProtectedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "You are authenticated!"})


class SendOTPView(APIView):
    """
    {
    "phone_number":"7736448062"
    }
    """
    permission_classes = [AllowAny]
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, created = Customer.objects.get_or_create(phone_number=phone_number)
            print("User object from Send OTPView",user)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp()

        OTP.objects.update_or_create(user=user, defaults={'otp': otp})

        print("OTP is:" , otp)
        send_otp(phone_number, otp)

        return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)
    
class VerifyOTPView(APIView):
    """
    {
    "phone_number":"7736448062",
    "otp":"593188"
    }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        print("ABCD EEEEEEEEEEEEEEEEEEEE")
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            return Response({"error": "Phone number and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Unpack the tuple correctly
            user, created = Customer.objects.get_or_create(phone_number=phone_number)
        except Customer.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Fetch OTP instance linked to the user
            otp_instance = OTP.objects.filter(user=user).first()

            if not otp_instance:
                return Response({"error": "OTP not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check OTP validity
            if otp_instance.otp == otp:
                tokens = TokenObtainPairSerializer.get_token(user)
                access_token = str(tokens.access_token)
                refresh_token = str(tokens)   
                return Response({
                        "message": "OTP verified successfully!",
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }, status=status.HTTP_200_OK)
                # if (now() - otp_instance.created_at).seconds < 300:  # 5-minute expiry
                #     user.is_active = True
                #     user.save()

                #     # Generate JWT tokens
                #     tokens = TokenObtainPairSerializer.get_token(user)
                #     access_token = str(tokens.access_token)
                #     refresh_token = str(tokens)                   
                # else:
                #     return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        except Customer.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CategoryCreateView(APIView):
    """
        {
        "name": "Electronics",
        "slug": "electronics",
        "parent": null,
        "description": "All kinds of electronic items",
        "image": null,
        "is_active": true,
        "meta_title": "Best Electronics",
        "meta_description": "Find the best electronics at great prices"
        }
    """
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProductCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Use the ProductSerializer to validate and save data
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductDetailView(APIView):
    permission_classes = [AllowAny]  # You can modify permissions based on your needs

    def get(self, request, *args, **kwargs):
        # Retrieve the product using the product ID (primary key)
        product_id = kwargs.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the product data along with its variants and images
        serializer = ProductSerializer(product)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProductCategoryView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, category_slug, *args, **kwargs):
        # Fetch the category based on the provided slug
        category = Category.objects.filter(slug=category_slug).first()
        if category is None:
            return Response({"detail": "Category not found."}, status=404)

        # Get all products that belong to this category
        products = Product.objects.filter(category=category)

        # Serialize the product data
        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)
    
class CategoryListView(APIView):
    permission_classes = [AllowAny]  # Modify permissions as per your requirements

    def get(self, request, *args, **kwargs):
        # Fetch top-level categories (those without a parent)
        top_level_categories = Category.objects.filter(parent=None)

        # Serialize the categories, which will include their children
        serializer = CategorySerializer(top_level_categories, many=True)
        
        return Response(serializer.data)
    
class CartProductRecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user  # Assuming the user is logged in

        # Get all the cart items for the user
        cart_items = Cart.objects.filter(user=user)

        # Extract product variants from the cart
        cart_product_variants = cart_items.values_list('product_variant', flat=True)

        # Get all categories from the products in the cart
        categories_in_cart = ProductVariant.objects.filter(id__in=cart_product_variants).values_list('product__category', flat=True)

        # Get all products from those categories, excluding already taken products
        # Limiting the number of products per cycle (e.g., 3 products per batch)
        batch_size = 3
        recommended_products = []

        for category_id in categories_in_cart:
            category = Category.objects.get(id=category_id)
            # Fetch products from this category excluding products already in the cart
            products_in_category = Product.objects.filter(category=category).exclude(
                variants__in=cart_product_variants).distinct()

            # Add up to 3 products from the category
            for product in products_in_category[:batch_size]:
                recommended_products.append(product)

        # Serialize the recommended products
        product_serializer = ProductSerializer(recommended_products, many=True)

        return Response(product_serializer.data)
    
class PreviousOrderProductRecommendationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user = request.user  # Assuming the user is logged in

        # Get the most recent order for the user (excluding cancelled orders)
        recent_order = Order.objects.filter(user=user, status__ne='Cancelled').order_by('-created_at').first()
        
        if not recent_order:
            return Response({"message": "No previous order found."}, status=404)

        # Extract the product variants from the previous order
        previous_order_items = OrderItem.objects.filter(order=recent_order)
        cart_product_variants = previous_order_items.values_list('product_variant', flat=True)

        # Get the categories of the products in the previous order
        categories_in_previous_order = ProductVariant.objects.filter(id__in=cart_product_variants).values_list('product__category', flat=True)

        # Limiting the number of products per cycle (e.g., 3 products per batch)
        batch_size = 3
        recommended_products = []

        for category_id in categories_in_previous_order:
            category = Category.objects.get(id=category_id)
            # Fetch products from this category excluding products already in the previous order
            products_in_category = Product.objects.filter(category=category).exclude(
                variants__in=cart_product_variants).distinct()

            # Add up to 3 products from the category
            for product in products_in_category[:batch_size]:
                recommended_products.append(product)

        # Serialize the recommended products
        product_serializer = ProductSerializer(recommended_products, many=True)

        return Response(product_serializer.data)
    


class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users can add to cart

    def post(self, request):
        try:
            user = request.user  
            variant_id = request.data.get("variant_id")
            quantity = request.data.get("quantity", 1)

            # Validate variant_id
            if not variant_id:
                return Response({"error": "Product variant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

            # Validate quantity (ensure it's a positive integer)
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({"error": "Invalid quantity value"}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the product variant
            variant = get_object_or_404(ProductVariant, id=variant_id)

            # Check stock availability
            if not variant.is_in_stock() or variant.stock < quantity:
                return Response({"error": "Insufficient stock available"}, status=status.HTTP_400_BAD_REQUEST)

            # Get or create cart item
            cart_item, created = Cart.objects.get_or_create(user=user, product_variant=variant)

            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > variant.stock:
                    return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)
                cart_item.quantity = new_quantity
            else:
                cart_item.quantity = quantity
            
            cart_item.save()

            return Response({"message": "Added to cart successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        try:
            cart_items = Cart.objects.filter(user=self.request.user)
            if not cart_items.exists():
                raise NotFound("Your cart is empty.")
            return cart_items
        except Exception as e:
            raise NotFound(f"An error occurred: {str(e)}")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except NotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": "Something went wrong. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class UpdateCartItemView(APIView):
    permission_classes = [AllowAny]  # Only authenticated users can modify the cart

    def put(self, request, cart_id):
        try:
            user = request.user
            quantity = request.data.get("quantity")

            # Validate quantity
            if quantity is None:
                return Response({"error": "Quantity is required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                quantity = int(quantity)
            except ValueError:
                return Response({"error": "Quantity must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

            cart_item = get_object_or_404(Cart, id=cart_id, user=user)
            variant = cart_item.product_variant

            # If quantity is 0 or less, remove item from cart
            if quantity <= 0:
                cart_item.delete()
                return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)

            # Check stock before increasing quantity
            if quantity > cart_item.quantity and quantity > variant.stock:
                return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)

            # Update cart quantity
            cart_item.quantity = quantity
            cart_item.save()

            return Response({"message": "Cart updated successfully", "cart_item": CartSerializer(cart_item).data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class LowestPriceProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return (
            Product.objects.filter(is_active=True)
            .annotate(lowest_price=Min("variants__price"))  # Get lowest variant price for each product
            .order_by("lowest_price")[:20]  # Sort by price and limit to 20 products
        )
    
class CheckoutSummaryView(APIView):
    permission_classes = [IsAuthenticated]  # Only authenticated users can proceed

    def get(self, request):
        try:
            user = request.user
            cart_items = Cart.objects.filter(user=user)

            if not cart_items.exists():
                return Response({"error": "Your cart is empty."}, status=status.HTTP_404_NOT_FOUND)

            # Calculate total cart price
            total_price = sum(item.quantity * item.product_variant.price for item in cart_items)

            # Static delivery charge
            delivery_charge = 40

            # Total price after adding delivery charge
            total_after_delivery = total_price + delivery_charge

            return Response({
                "cart_items": CartSerializer(cart_items, many=True).data,
                "total_price": total_price,
                "delivery_charge": delivery_charge,
                "total_after_delivery": total_after_delivery
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"Something went wrong: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        payment_method = request.data.get("payment_method")
        delivery_address_id = request.data.get("delivery_address")

        # Fetch cart items
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        # Generate unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:10].upper()}"

        # Calculate total price
        total_price = sum(item.quantity * item.product_variant.price for item in cart_items)
        delivery_charge = 40  # Static charge
        total_amount = total_price + delivery_charge

        with transaction.atomic():  # Ensures all operations succeed or fail together
            # Create order
            order = Order.objects.create(
                user=user,
                order_number=order_number,
                total_amount=total_amount,
                payment_method=payment_method,
                delivery_address_id=delivery_address_id
            )

            # Move cart items to order items
            order_items = []
            for cart_item in cart_items:
                order_items.append(OrderItem(
                    order=order,
                    product_variant=cart_item.product_variant,
                    quantity=cart_item.quantity,
                    price_per_item=cart_item.product_variant.price,
                    total_price=cart_item.quantity * cart_item.product_variant.price
                ))

            OrderItem.objects.bulk_create(order_items)  # Efficiently insert all items

            # Clear the cart after successful order creation
            cart_items.delete()

        return Response({
            "message": "Order placed successfully!",
            "order_number": order.order_number,
            "total_amount": total_amount
        }, status=status.HTTP_201_CREATED)
    

# ✅ **Create a Review**
class AddReviewView(generics.CreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]  # User must be logged in

    def perform_create(self, serializer):
        product_id = self.request.data.get("product")  # Get product ID from request
        product = Product.objects.get(id=product_id)  # Fetch product
        serializer.save(user=self.request.user, product=product)  # Save review

# ✅ **List Reviews for a Product**
class ProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [AllowAny]  # Anyone can view reviews

    def get_queryset(self):
        product_id = self.kwargs["product_id"]  # Get product ID from URL
        return ProductReview.objects.filter(product_id=product_id).order_by("-created_at")