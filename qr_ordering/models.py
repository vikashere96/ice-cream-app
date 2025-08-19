import qrcode
from io import BytesIO
from django.core.files import File
from django.db import models
import uuid
import time



class IceCream(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='ice_cream_images/')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Push product data to Firebase Database with local image URL
        try:
            from firebase_admin import db
            if self.image:
                image_url = self.image.url  # Local media URL
                db.reference(f'products/{self.id}').set({
                    'name': self.name,
                    'price': float(self.price),
                    'image_url': image_url
                })
        except Exception as e:
            print(f"Error pushing IceCream data to Firebase: {e}")

class Table(models.Model):

    number = models.PositiveIntegerField(unique=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    qr_base_url = models.URLField(
        max_length=200,
        blank=True,
        default='',
        help_text="Base URL for QR code (e.g. https://yourdomain.com)"
    )

    def __str__(self):
        return f"Table {self.number}"

    def save(self, *args, **kwargs):
        # Determine if QR must be regenerated
        need_regenerate = False
        previous = None
        if self.pk:
            try:
                previous = Table.objects.only('qr_base_url', 'token', 'number', 'qr_code').get(pk=self.pk)
            except Table.DoesNotExist:
                previous = None

        if not self.qr_code:
            need_regenerate = True
        elif previous and (
            previous.qr_base_url != self.qr_base_url or
            previous.token != self.token or
            previous.number != self.number
        ):
            need_regenerate = True

        if need_regenerate:
            # Prefer model-specific base URL, then project-wide SITE_BASE_URL
            try:
                from django.conf import settings
                default_base = getattr(settings, 'SITE_BASE_URL', 'http://127.0.0.1:8000')
            except Exception:
                default_base = 'http://127.0.0.1:8000'
            base_url = (self.qr_base_url or default_base).rstrip('/')
            qr_url = f"{base_url}/table/{str(self.token)}/"

            # Remove old file to avoid stale caches
            if self.qr_code:
                try:
                    self.qr_code.delete(save=False)
                except Exception:
                    pass

            qr_image = qrcode.make(qr_url)
            buffer = BytesIO()
            qr_image.save(buffer, 'PNG')
            # Use timestamped filename to bust caches
            file_name = f'table-{self.number}-qr-{int(time.time())}.png'
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)

        # Push table data to Firebase Database with local QR code image URL
        try:
            from firebase_admin import db
            if self.qr_code:
                qr_code_url = self.qr_code.url  # Local media URL
                db.reference(f'tables/{self.id}').set({
                    'number': self.number,
                    'token': str(self.token),
                    'qr_code_url': qr_code_url
                })
        except Exception as e:
            print(f"Error pushing Table data to Firebase: {e}")

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} for Table {self.table.number}"
    
    def get_total_amount(self):
        """Calculate the total amount for this order"""
        total = 0
        for item in self.items.all():
            total += item.quantity * item.ice_cream.price
        return total

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    ice_cream = models.ForeignKey(IceCream, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.ice_cream.name}"
