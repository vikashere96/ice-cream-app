from django.contrib import admin
from .models import IceCream, Table, Order, OrderItem, Refund, EmailVerification
from django.utils.html import format_html
import qrcode
import io
import base64
from django.core.signing import Signer

signer = Signer()

class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'qr_code_thumbnail')

    def qr_code_thumbnail(self, obj):
        if obj.qr_code:
            return format_html(f'<img src="{obj.qr_code.url}" width="100" />')
        return "No QR Code"
    qr_code_thumbnail.short_description = "QR Code"

class RefundAdmin(admin.ModelAdmin):
    list_display = ('order', 'customer_name', 'customer_email', 'refund_amount', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'order__id')
    readonly_fields = ('created_at',)

class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_verified', 'created_at', 'verified_at', 'expires_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('created_at', 'verified_at')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_email', 'table', 'status', 'payment_status', 'created_at', 'paid_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'id')
    readonly_fields = ('created_at', 'paid_at')

admin.site.register(IceCream)
admin.site.register(Table, TableAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Refund, RefundAdmin)
admin.site.register(EmailVerification, EmailVerificationAdmin)
