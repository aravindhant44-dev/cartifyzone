from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    delete_order,
    first_page,
    home,
    product_detail,
    add_to_cart,
    cart,
    increase_quantity,
    decrease_quantity,
    profile,
    orders,
    remove_from_cart,
    checkout,
    success,
    register,
    user_login,
    user_logout,
)


urlpatterns = [
    path('', first_page, name='first_page'),
    path('home/', home, name='home'),

    path('register/', register, name='register'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),

    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('delete-order/<int:order_id>/', delete_order, name='delete_order'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/', cart, name='cart'),
    path('increase/<int:cart_id>/', increase_quantity, name='increase_quantity'),
    path('decrease/<int:cart_id>/', decrease_quantity, name='decrease_quantity'),
    path('remove/<int:cart_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('success/', success, name='success'),
    path('profile/', profile, name='profile'),
    path('orders/', orders, name='orders'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )