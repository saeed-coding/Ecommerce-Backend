"""
URL configuration for ecommerce_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from product.views import *
from users.views import *


urlpatterns = [
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
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
