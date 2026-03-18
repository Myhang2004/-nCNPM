from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    # API
    path('api/products/', views.api_products, name="api_products"),
    path('api/add-product/', views.api_add_product, name="api_add_product"),
    path('api/delete-product/<int:id>/', views.api_delete_product),
    path('api/categories/', views.api_categories, name="api_categories"),
    path('api/cart/', views.api_cart, name="api_cart"),
    path('api/update_item/', views.api_update_cart, name="api_update_cart"),
    path('api/register/', views.api_register, name="api_register"),
    path('api/logout/', views.api_logout),
    path('api/login/', views.api_login, name="api_login"),
    path('api/users/', views.api_users, name="api_users"),
    path('api/product/<int:id>/', views.api_product_detail, name="api_product_detail"),
    path('api/orders/', views.api_orders, name="api_orders"),
    path('api/order/<int:order_id>/', views.api_order_detail, name="api_order_detail"),
    path('api/search/', views.api_search, name="api_search"),


    path('', views.home, name="home"),  # Render home view
    path('register/', views.register, name="register" ),
    path('login/', views.loginPage, name="login" ),
    path('search/', views.search, name="search" ),
    path('category/', views.category, name="category" ),
    path('detail/', views.detail, name="detail" ),
    path('logout/', views.logoutPage, name="logout" ),
    path('cart/', views.cart, name="cart" ),
    path('checkout/', views.checkout, name="checkout" ),
    path('update_item/', views.updateItem, name="update_item" ),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),
    path('order-history/', views.order_history, name='order_history'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('dashboard/<int:order_id>/', views.dashboard, name='dashboard'),

    # CHAT
    path('chat/', views.chat_api, name="chat"),
    path('messages/', views.get_messages),
    path('admin-send/', views.admin_send),

]

