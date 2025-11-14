from django.urls import path
from . import views

urlpatterns = [
    # Customer facing
    path('table/<str:token>/', views.order_page, name='order_page'),
    path('order/submit/', views.submit_order, name='submit_order'),
    path('customer/google-login/', views.customer_google_login, name='customer_google_login'),
    path('customer/verify-email/', views.verify_email, name='verify_email'),
    path('customer/resend-verification/', views.resend_verification, name='resend_verification'),
    path('order/status/<int:order_id>/', views.order_status, name='order_status'),
    path('order/success/', views.order_success, name='order_success'),
    path('payment/verify/', views.verify_payment, name='verify_payment'),
    path('payment/status/<int:order_id>/', views.check_payment_status, name='check_payment_status'),
    path('debug/login/', views.debug_login, name='debug_login'),
    path('api/orders/', views.get_orders_json, name='get_orders_json'),
    path('panel/dashboard/simple/', views.admin_dashboard_simple, name='admin_dashboard_simple'),
    
    # Customer order lookup for refunds
    path('customer/orders/', views.customer_orders, name='customer_orders'),
    path('customer/order/<int:order_id>/refund/', views.customer_refund_request, name='customer_refund_request'),

    # Admin
    path('panel/login/', views.admin_login, name='admin_login'),
    path('panel/logout/', views.admin_logout, name='admin_logout'),
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/analytics/', views.admin_analytics, name='admin_analytics'),
    path('panel/settings/', views.admin_settings, name='admin_settings'),
    path('panel/order/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('panel/order/<int:order_id>/details/', views.order_details, name='order_details'),
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
    
    # Refund Management
    path('panel/order/<int:order_id>/refund/', views.process_refund, name='process_refund'),
    path('panel/refunds/', views.refund_list, name='refund_list'),
    path('panel/refund/<int:refund_id>/update/', views.update_refund_status, name='update_refund_status'),
]
