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
    seats = models.PositiveIntegerField(default=4, help_text="Number of seats at this table")
    description = models.TextField(blank=True, help_text="Optional description or location of the table")
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

class EmailVerification(models.Model):
    email = models.EmailField()
    verification_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"Verification for {self.email}"
    
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

class Order(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),  # Order created but payment not initiated
        ('pending_payment', 'Pending Payment'),
        ('paid', 'Paid'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='orders')
    customer_email = models.EmailField(default='customer@example.com')
    customer_name = models.CharField(max_length=100, default='Customer')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_payment')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

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

class Refund(models.Model):
    REFUND_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='refund')
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=100)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer')
    payment_details = models.TextField(blank=True, default="Refund will be processed to your original payment method")
    refund_reason = models.TextField(blank=True, default="Item not available")
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"Refund for Order #{self.order.id} - ₹{self.refund_amount}"


class ShopSettings(models.Model):
    """Store-wide settings for the ice cream shop"""
    # General Settings
    shop_name = models.CharField(max_length=200, default='Ice Cream Shop')
    shop_description = models.TextField(blank=True, default='Premium ice cream shop serving delicious flavors')
    phone = models.CharField(max_length=20, blank=True, default='+1 (555) 123-4567')
    email = models.EmailField(blank=True, default='info@icecreamshop.com')
    address = models.TextField(blank=True, default='123 Sweet Street, Ice Cream City')
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    
    # Currency & Format
    currency = models.CharField(max_length=10, default='INR', choices=[
        ('USD', 'USD ($)'),
        ('EUR', 'EUR (€)'),
        ('GBP', 'GBP (£)'),
        ('INR', 'INR (₹)'),
    ])
    timezone = models.CharField(max_length=50, default='Asia/Kolkata')
    date_format = models.CharField(max_length=20, default='DD/MM/YYYY')
    order_prefix = models.CharField(max_length=10, default='ICE')
    
    # Payment Settings
    upi_enabled = models.BooleanField(default=True)
    upi_id = models.CharField(max_length=100, blank=True, default='your-upi-id@bank')
    upi_merchant_name = models.CharField(max_length=100, blank=True, default='Your Shop Name')
    
    razorpay_enabled = models.BooleanField(default=False)
    razorpay_key_id = models.CharField(max_length=100, blank=True)
    razorpay_key_secret = models.CharField(max_length=100, blank=True)
    
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Email Settings
    smtp_host = models.CharField(max_length=100, default='smtp.gmail.com')
    smtp_port = models.IntegerField(default=587)
    from_email = models.EmailField(default='your-email@gmail.com')
    from_name = models.CharField(max_length=100, default='Your Shop Name')
    email_password = models.CharField(max_length=200, blank=True)
    email_verification_required = models.BooleanField(default=True)
    
    # Notification Settings
    notify_new_orders = models.BooleanField(default=True)
    notify_payments = models.BooleanField(default=True)
    notify_refunds = models.BooleanField(default=True)
    admin_notification_email = models.EmailField(blank=True, default='admin@icecreamshop.com')
    
    # Daily Reports
    daily_report_enabled = models.BooleanField(default=False)
    daily_report_time = models.TimeField(null=True, blank=True)
    
    # Backup Settings
    auto_backup_enabled = models.BooleanField(default=False)
    backup_time = models.TimeField(null=True, blank=True)
    
    # System Settings
    auto_refresh_dashboard = models.BooleanField(default=True)
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        verbose_name = 'Shop Settings'
        verbose_name_plural = 'Shop Settings'
    
    def __str__(self):
        return f"Settings for {self.shop_name}"
    
    @classmethod
    def get_settings(cls):
        """Get or create settings instance"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
