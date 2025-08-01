from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.http import JsonResponse
from product.views import *
from users.views import *

def home(request):
    return JsonResponse({"message": "Welcome to the API!"})


urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('add_product/', add_product, name='add_product'),
    path('add_variations/', add_variations, name='add_variations'),
    path('get_product/', get_product, name='get_product'),
    path('update_product/', update_product, name='update_product'),
    path('delete_product/', delete_product, name='delete_product'),
    path('get_all_categories/', get_all_categories, name='get_all_categories'),
    path('get_product_types/', get_product_types, name='get_product_types'),
    path('search_products/', search_products, name='search_products'),
    path('add_sale_order/', add_sale_order, name='add_sale_order'),
    path('login/', LoginUser.as_view(), name='login'),
    path('register/', RegisterUser.as_view(), name='register'),
    path('logout/', LogoutUser.as_view(), name='logout'),
    path('add_product_images/', add_product_images, name='add_product_images'),
    path('delete_product_image/', delete_product_image, name='delete_product_image'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
