from django.urls import path
from . import views

urlpatterns = [
    # Customer facing
    path('table/<str:token>/', views.order_page, name='order_page'),
    path('order/submit/', views.submit_order, name='submit_order'),
    path('customer/google-login/', views.customer_google_login, name='customer_google_login'),
    path('order/status/<int:order_id>/', views.order_status, name='order_status'),
    path('order/success/', views.order_success, name='order_success'),

    # Admin
    path('panel/login/', views.admin_login, name='admin_login'),
    path('panel/logout/', views.admin_logout, name='admin_logout'),
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/order/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('panel/orders/clear/', views.clear_all_orders, name='clear_all_orders'),
    path('panel/order/<int:order_id>/delete/', views.delete_order, name='delete_order'),
    
    # Ice Cream Management
    path('panel/ice-creams/', views.manage_ice_creams, name='manage_ice_creams'),
    path('panel/ice-creams/add/', views.add_ice_cream, name='add_ice_cream'),
    path('panel/ice-creams/edit/<int:pk>/', views.edit_ice_cream, name='edit_ice_cream'),
    path('panel/ice-creams/delete/<int:pk>/', views.delete_ice_cream, name='delete_ice_cream'),

    # Table Management
    path('panel/tables/', views.manage_tables, name='manage_tables'),
    path('panel/tables/add/', views.add_table, name='add_table'),
    path('panel/tables/edit/<int:pk>/', views.edit_table, name='edit_table'),
    path('panel/tables/delete/<int:pk>/', views.delete_table, name='delete_table'),
]
