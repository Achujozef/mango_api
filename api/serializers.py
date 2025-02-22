from rest_framework import serializers
from .models import OTP,Category,Product,ProductVariant,Cart,ProductReview,ProductImage

class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
    def get_children(self, obj):
        # This method recursively fetches child categories
        children = Category.objects.filter(parent=obj)
        return CategorySerializer(children, many=True).data

class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(many=True)  # List of variants for the product
    images = ImageSerializer(many=True)  # List of images for the variants

    class Meta:
        model = Product
        fields = '__all__'

    def create(self, validated_data):
        variants_data = validated_data.pop('variants')
        images_data = validated_data.pop('images')
        
        # Create the Product
        product = Product.objects.create(**validated_data)
        
        # Create variants and link to the product
        for variant_data in variants_data:
            variant_data['product'] = product  # Link the variant to the product
            ProductVariant.objects.create(**variant_data)
        
        # Create images and link to the corresponding variant
        for image_data in images_data:
            ProductImage.objects.create(**image_data)
        
        return product
    
class CartSerializer(serializers.ModelSerializer):
    product_variant = ProductVariantSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'product_variant', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.quantity * obj.product_variant.price

class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)  # Display username instead of ID

    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']