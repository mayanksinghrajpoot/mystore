from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Categories
    path('categories/', views.category_list, name='admin_category_list'),
    path('categories/add/', views.category_add, name='admin_category_add'),
    path('categories/edit/<int:pk>/', views.category_edit, name='admin_category_edit'),
    path('categories/delete/<int:pk>/', views.category_delete, name='admin_category_delete'),

    # Products
    path('products/', views.product_list, name='admin_product_list'),
    path('products/add/', views.product_add, name='admin_product_add'),
    path('products/edit/<int:pk>/', views.product_edit, name='admin_product_edit'),
    path('products/delete/<int:pk>/', views.product_delete, name='admin_product_delete'),
    
    # Orders
    path('orders/', views.order_list, name='admin_order_list'),
    path('orders/<int:pk>/', views.order_detail, name='admin_order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='admin_order_update_status'),
]
