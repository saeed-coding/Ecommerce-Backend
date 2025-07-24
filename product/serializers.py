from rest_framework import serializers
from .models import Product, ProductImage, SaleItem, Sale, ProductVariation
# from .models import Product, ProductImage, Sale, ProductVariation


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = "__all__"


class SaleItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    variation_id = serializers.PrimaryKeyRelatedField(queryset=ProductVariation.objects.all(), allow_null=True)
    class Meta:
        model = SaleItem
        fields = "__all__"
        extra_kwargs = {
            'sale_id': {'read_only': True}  # ✅ This avoids expecting it in input
        }


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = "__all__"


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = "__all__"
