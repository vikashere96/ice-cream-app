from django.contrib import admin
from .models import IceCream, Table, Order, OrderItem
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

admin.site.register(IceCream)
admin.site.register(Table, TableAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
