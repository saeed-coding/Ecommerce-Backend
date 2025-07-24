from django.db import models


class Product(models.Model):
    title = models.TextField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100)
    discount = models.IntegerField(default=0)
    is_discounted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"Image for {self.product}"


class ProductVariation(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    sku = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product_id.title} - {self.sku}"


class Sale(models.Model):
    user = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    area = models.CharField(max_length=150, blank=True, null=True)
    province = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    mail = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    coupon_code = models.CharField(max_length=50, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Order #{self.pk} by {self.user}"


class SaleItem(models.Model):
    sale_id = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product_id = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variation_id = models.ForeignKey(ProductVariation, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

