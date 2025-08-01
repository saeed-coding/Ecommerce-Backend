from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, ProductImage, ProductVariation, Sale, SaleItem

from .serializers import *
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db import transaction


class IsAdminUserCustom(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def add_product(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()

        # Add images if present
        images_data = request.data.get('images', [])
        for img in images_data:
            ProductImage.objects.create(product=product, image=img)

        # Add variations if present
        variations_data = request.data.get('variations', [])
        for var in variations_data:
            ProductVariation.objects.create(product=product, **var)

        return Response({'message': 'Product created successfully', 'product_id': product.id},
                        status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def add_variations(request):
    serializer = ProductVariationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_product(request):
    product_id = request.GET.get('id')
    title = request.GET.get('title')
    category = request.GET.get('category')
    product_type = request.GET.get('product_type')
    try:
        if product_id:
            product = Product.objects.filter(id=product_id)
        elif title:
            product = Product.objects.filter(title__icontains=title)
        elif category:
            product = Product.objects.filter(category=category)
        elif product_type:
            product = Product.objects.filter(product_type=product_type)
        else:
            product = Product.objects.all()
        if product:
            data = []
            for p in product:
                product_data = ProductSerializer(p).data
                product_data['images'] = ProductImageSerializer(p.images.all(), many=True).data
                product_data['variations'] = ProductVariationSerializer(p.variations.all(), many=True).data
                data.append(product_data)
            return Response(data)
        else:
            return Response({'error': 'Product not found'}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def update_product(request):
    id = request.data.get('id')
    try:
        product = Product.objects.get(id=id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response({'error': 'Not found'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def delete_product(request):
    id = request.data.get('id')
    category = request.data.get('category')
    product_type = request.data.get('product_type')

    try:
        if id:
            products = Product.objects.filter(id=id)
        elif category:
            products = Product.objects.filter(category=category)
        elif product_type:
            products = Product.objects.filter(product_type=product_type)
        else:
            return Response({"error": "No valid parameter provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not products.exists():
            return Response({"error": "No products found"}, status=status.HTTP_404_NOT_FOUND)

        count = products.count()
        products.delete()
        return Response({"message": f"Deleted {count} product(s) successfully"}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_all_categories(request):
    categories = Product.objects.values_list('category', flat=True).distinct()
    return Response(categories)


@api_view(['GET'])
def get_product_types(request):
    category = request.GET.get('category')
    try:
        products = Product.objects.filter(category=category)
        if products:
            product_types = products.values_list('product_type', flat=True).distinct()
            return Response(product_types)
        else:
            return Response({"error": f"Not Found Product Types for {category}"})
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def search_products(request):
    title_query = request.GET.get('title', '')
    products = Product.objects.filter(title__icontains=title_query)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_sale_order(request):
    data = request.data
    items_data = data.pop('items', [])

    # Validate main sale
    sale_serializer = SaleSerializer(data=data)
    if not sale_serializer.is_valid():
        return Response({"error": "Invalid sale data", "details": sale_serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    # Save the sale first
    sale = sale_serializer.save()

    # Validate each sale item individually
    errors = []
    for item in items_data:
        item['sale_id'] = sale.pk  # attach FK
        item_serializer = SaleItemSerializer(data=item)
        if item_serializer.is_valid():
            item_serializer.save(sale_id=sale)
        else:
            errors.append(item_serializer.errors)

    # If any item has error, rollback
    if errors:
        sale.delete()
        return Response({"error": "Invalid sale item data", "details": errors},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({"message": "Order created successfully", "sale_id": sale.id},
                    status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
@parser_classes([MultiPartParser, FormParser])
def add_product_images(request):
    product_id = request.data.get('product_id')
    if not product_id:
        return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    files = request.FILES.getlist('images')
    if not files:
        return Response({"error": "At least one image file is required (key: images)"},
                        status=status.HTTP_400_BAD_REQUEST)

    created_images = []
    try:
        with transaction.atomic():
            for file in files:
                img = ProductImage.objects.create(product=product, image=file)
                created_images.append(ProductImageSerializer(img, context={'request': request}).data)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "message": f"Added {len(created_images)} image(s) to product {product.id}",
        "product_id": product.id,
        "images": created_images
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUserCustom])
def delete_product_image(request):
    image_id = request.data.get('image_id')
    if not image_id:
        return Response({"error": "image_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        img = ProductImage.objects.get(id=image_id)
    except ProductImage.DoesNotExist:
        return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

    # delete the binary from storage first
    if img.image:
        img.image.delete(save=False)

    img.delete()
    return Response({"message": "Image deleted"}, status=status.HTTP_200_OK)


