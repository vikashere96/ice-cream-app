# qr_ordering/views.py

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import IceCream, Table, Order, OrderItem, Refund, EmailVerification
from .forms import IceCreamForm, TableForm, RefundForm
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from firebase_admin import db
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, F
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import random
import string
from datetime import timedelta


def order_page(request, token):
    from django.conf import settings
    
    table = get_object_or_404(Table, token=token)
    
    # Get all ice creams and handle missing images gracefully
    ice_creams = IceCream.objects.all()
    
    # Filter out ice creams with missing or invalid images
    valid_ice_creams = []
    for ice_cream in ice_creams:
        try:
            # Try to access the image URL to check if it exists
            if ice_cream.image and ice_cream.image.url:
                valid_ice_creams.append(ice_cream)
            else:
                # Ice cream without image - still include it, template will handle placeholder
                valid_ice_creams.append(ice_cream)
        except (ValueError, AttributeError):
            # Image field exists but file is missing - still include it
            valid_ice_creams.append(ice_cream)
    
    customer_name = request.session.get('customer_name')
    customer_picture = request.session.get('customer_picture')
    
    # Get UPI settings from environment
    upi_merchant_id = os.environ.get('UPI_MERCHANT_ID', 'your-upi-id@bank')
    upi_merchant_name = os.environ.get('UPI_MERCHANT_NAME', 'Your Shop Name')
    
    return render(request, 'order_page.html', {
        'table': table,
        'ice_creams': valid_ice_creams,
        'customer_name': customer_name,
        'customer_picture': customer_picture,
        'customer_email': request.session.get('customer_email', ''),
        'email_verified': request.session.get('email_verified', False),
        'razorpay_key': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'upi_merchant_id': upi_merchant_id,
        'upi_merchant_name': upi_merchant_name,
    })
from django.views.decorators.csrf import csrf_exempt
import requests
# Google login endpoint for customer
@csrf_exempt
def customer_google_login(request):
    import json
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Check if this is a manual login (email + name provided directly)
        if data.get('manual_login'):
            email = data.get('email')
            name = data.get('name')
            picture = 'https://via.placeholder.com/40'
            
            if not email or not name:
                return JsonResponse({'success': False, 'error': 'Email and name required'}, status=400)
        else:
            # Original Google OAuth flow
            token = data.get('credential')
            if not token:
                return JsonResponse({'success': False, 'error': 'No credential provided'}, status=400)
                
            # Verify token with Google
            google_response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
            if google_response.status_code != 200:
                return JsonResponse({'success': False, 'error': 'Invalid Google token'}, status=400)
                
            info = google_response.json()
            name = info.get('name')
            picture = info.get('picture')
            email = info.get('email')
        
        if not email or not name:
            return JsonResponse({'success': False, 'error': 'Missing email or name from login'}, status=400)
        
        # Normalize email
        email = email.lower().strip()
        
        # Send email verification
        verification_code = generate_verification_code()
        expires_at = timezone.now() + timedelta(minutes=10)
        
        # Clean up old unverified records for this email
        EmailVerification.objects.filter(email=email, is_verified=False).delete()
        
        # Create new verification record
        verification = EmailVerification.objects.create(
            email=email,
            verification_code=verification_code,
            expires_at=expires_at
        )
        
        print(f"DEBUG: Created verification record - Email: {email}, Code: {verification_code}")
        
        # Send verification email
        try:
            send_verification_email(email, name, verification.verification_code)
            
            # Store in session (but mark as unverified)
            request.session['customer_name'] = name
            request.session['customer_picture'] = picture
            request.session['customer_email'] = email
            request.session['email_verified'] = verification.is_verified
            
            return JsonResponse({
                'success': True, 
                'name': name, 
                'picture': picture, 
                'email': email,
                'email_verified': verification.is_verified,
                'verification_sent': True
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to send verification email: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, name, code):
    """Send email verification code"""
    subject = 'Verify Your Email - Ice Cream Shop'
    
    html_message = render_to_string('emails/email_verification.html', {
        'name': name,
        'code': code,
    })
    
    plain_message = f"""
    Hi {name},
    
    Your verification code is: {code}
    
    This code will expire in 10 minutes.
    
    Thank you,
    Ice Cream Shop
    """
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        html_message=html_message,
        fail_silently=False,
    )

@csrf_exempt
def verify_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
        code = data.get('code', '').strip()
        
        print(f"DEBUG: Verification attempt - Email: {email}, Code: {code}")
        
        # Check for test code first (for development/testing)
        if code == '123456':
            # Find any verification record for this email
            try:
                verification = EmailVerification.objects.filter(email=email, is_verified=False).first()
                if verification:
                    # Mark as verified with test code
                    verification.is_verified = True
                    verification.verified_at = timezone.now()
                    verification.save()
                    
                    # Update session
                    request.session['email_verified'] = True
                    
                    return JsonResponse({'success': True, 'message': 'Email verified successfully (test code)'})
                else:
                    # Create a verification record if none exists
                    verification = EmailVerification.objects.create(
                        email=email,
                        verification_code='123456',
                        is_verified=True,
                        verified_at=timezone.now(),
                        expires_at=timezone.now() + timedelta(hours=1)
                    )
                    
                    # Update session
                    request.session['email_verified'] = True
                    
                    return JsonResponse({'success': True, 'message': 'Email verified successfully (test code)'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Test verification failed: {str(e)}'}, status=400)
        
        # Normal verification flow
        try:
            # Debug: Check all verification records for this email
            all_verifications = EmailVerification.objects.filter(email=email)
            print(f"DEBUG: Found {all_verifications.count()} verification records for {email}")
            
            for v in all_verifications:
                print(f"DEBUG: Record - Code: {v.verification_code}, Verified: {v.is_verified}, Expired: {v.is_expired()}")
            
            verification = EmailVerification.objects.get(
                email=email,
                verification_code=code,
                is_verified=False
            )
            
            print(f"DEBUG: Found matching verification record")
            
            if verification.is_expired():
                print(f"DEBUG: Verification code has expired")
                return JsonResponse({'success': False, 'error': 'Verification code has expired'}, status=400)
            
            # Mark as verified
            verification.is_verified = True
            verification.verified_at = timezone.now()
            verification.save()
            
            print(f"DEBUG: Email verified successfully")
            
            # Update session
            request.session['email_verified'] = True
            
            return JsonResponse({'success': True, 'message': 'Email verified successfully'})
            
        except EmailVerification.DoesNotExist:
            print(f"DEBUG: No matching verification record found")
            return JsonResponse({'success': False, 'error': 'Invalid verification code'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@csrf_exempt
def resend_verification(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        
        try:
            verification = EmailVerification.objects.get(email=email, is_verified=False)
            
            # Check if 2 minutes have passed since last code was sent
            time_since_created = timezone.now() - verification.created_at
            if time_since_created < timedelta(minutes=2):
                remaining_seconds = 120 - int(time_since_created.total_seconds())
                return JsonResponse({
                    'success': False, 
                    'error': f'Please wait {remaining_seconds} seconds before requesting a new code'
                }, status=429)
            
            # Generate new code
            verification.verification_code = generate_verification_code()
            verification.expires_at = timezone.now() + timedelta(minutes=10)
            verification.created_at = timezone.now()  # Update created_at for rate limiting
            verification.save()
            
            # Send new verification email
            name = request.session.get('customer_name', 'Customer')
            send_verification_email(email, name, verification.verification_code)
            
            return JsonResponse({'success': True, 'message': 'Verification code resent'})
            
        except EmailVerification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Email not found'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Failed to resend: {str(e)}'}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def submit_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_id = data['table_id']
        items = data['items']

        # Check if email is verified (temporarily disabled for testing)
        if not request.session.get('email_verified', False):
            return JsonResponse({'status': 'error', 'error': 'Email verification required'}, status=400)
        
        # Get customer details from session (with fallbacks for testing)
        customer_email = request.session.get('customer_email', 'customer@example.com')
        customer_name = request.session.get('customer_name', 'Customer')
        
        if not customer_email or not customer_name:
            return JsonResponse({'status': 'error', 'error': 'Customer information missing'}, status=400)

        table = get_object_or_404(Table, id=table_id)
        
        # Create order with customer details (draft status until payment confirmed)
        order = Order.objects.create(
            table=table,
            customer_email=customer_email,
            customer_name=customer_name,
            status='draft'  # Draft status until payment is confirmed
        )
        
        for item in items:
            ice_cream = get_object_or_404(IceCream, id=item['id'])
            OrderItem.objects.create(
                order=order,
                ice_cream=ice_cream,
                quantity=item['quantity']
            )
        
        # Prepare order payload for Firebase and status URL
        order_data = {
            'id': order.id,
            'table': order.table.number,
            'customer_email': order.customer_email,
            'customer_name': order.customer_name,
            'status': order.get_status_display(),
            'payment_status': order.get_payment_status_display(),
            'created_at': order.created_at.isoformat(),
            'total_amount': float(order.get_total_amount()),
            'items': [{'quantity': item.quantity, 'name': item.ice_cream.name, 'price': float(item.ice_cream.price)} for item in order.items.all()]
        }
        status_url = reverse('order_status', kwargs={'order_id': order.id})
        
        try:
            db.reference(f'orders/{order.id}').set(order_data)
            print(f"Order {order.id} synced to Firebase successfully")
        except Exception as e:
            print(f'Firebase error for order {order.id}: {e}')
            # Continue without Firebase - order is still saved in Django database
        
        return JsonResponse({'status': 'success', 'order_id': order.id, 'status_url': status_url})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def verify_payment(request):
    """Verify payment status - called by payment gateway webhook or polling"""
    if request.method == 'POST':
        data = json.loads(request.body)
        order_id = data.get('order_id')
        payment_reference = data.get('payment_reference')
        payment_method = data.get('payment_method', 'UPI')
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Update payment status and move from draft to paid
            order.payment_status = 'completed'
            order.status = 'paid'  # Move from draft -> paid (confirmed order)
            order.payment_reference = payment_reference
            order.payment_method = payment_method
            order.paid_at = timezone.now()
            order.save()
            
            # Send payment confirmation email
            try:
                send_payment_confirmation_email(order)
            except Exception as e:
                print(f"Failed to send payment confirmation email: {e}")
            
            # Update Firebase
            try:
                db.reference(f'orders/{order.id}').update({
                    'status': order.get_status_display(),
                    'payment_status': order.get_payment_status_display(),
                    'paid_at': order.paid_at.isoformat() if order.paid_at else None
                })
            except Exception as e:
                print(f'Firebase update error for order {order.id}: {e}')
            
            return JsonResponse({'status': 'success', 'message': 'Payment verified'})
            
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'error': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'error': 'Invalid request'}, status=400)

def customer_orders(request):
    """Customer order lookup for refunds - only shows paid orders"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            # Only show paid orders (not draft orders)
            orders = Order.objects.filter(
                customer_email=email,
                status__in=['paid', 'in_progress', 'completed']  # Exclude draft orders
            ).order_by('-created_at')
            return render(request, 'customer_orders.html', {
                'orders': orders,
                'email': email
            })
    
    return render(request, 'customer_orders.html')

def customer_refund_request(request, order_id):
    """Customer refund request form"""
    order = get_object_or_404(Order, id=order_id)
    
    # Only allow refunds for paid orders
    if order.status not in ['paid', 'in_progress', 'completed']:
        return JsonResponse({'error': 'Order not eligible for refund'}, status=400)
    
    if request.method == 'POST':
        # Create refund request
        refund = Refund.objects.create(
            order=order,
            refund_amount=order.get_total_amount(),
            customer_email=order.customer_email,
            customer_name=order.customer_name,
            refund_reason=request.POST.get('reason', 'Customer requested refund'),
            status='pending'
        )
        
        return JsonResponse({
            'status': 'success',
            'message': f'Refund request submitted for Order #{order.id}',
            'refund_id': refund.id
        })
    
    return render(request, 'customer_refund_form.html', {'order': order})

@csrf_exempt
@csrf_exempt
def debug_login(request):
    """Debug login for testing (remove in production)"""
    if request.method == 'POST':
        # Set debug session data
        request.session['customer_email'] = 'test@example.com'
        request.session['customer_name'] = 'Test Customer'
        request.session['customer_picture'] = 'https://via.placeholder.com/40'
        request.session['email_verified'] = True
        
        return JsonResponse({
            'success': True,
            'name': 'Test Customer',
            'email': 'test@example.com',
            'picture': 'https://via.placeholder.com/40',
            'email_verified': True
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def check_payment_status(request, order_id):
    """Check payment status for an order"""
    try:
        order = Order.objects.get(id=order_id)
        return JsonResponse({
            'status': 'success',
            'payment_status': order.payment_status,
            'order_status': order.status,
            'paid_at': order.paid_at.isoformat() if order.paid_at else None
        })
    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'error': 'Order not found'}, status=404)

def send_payment_confirmation_email(order):
    """Send payment confirmation email to customer"""
    subject = f'Payment Confirmed - Order #{order.id}'
    
    html_message = render_to_string('emails/payment_confirmation.html', {
        'order': order,
        'items': order.items.all(),
        'total': order.get_total_amount(),
    })
    
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer_email],
        html_message=html_message,
        fail_silently=False,
    )

def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_status.html', {'order': order})

@login_required
def admin_dashboard(request):
    today = timezone.now().date()
    
    # Get today's orders (exclude draft orders)
    orders_today = Order.objects.filter(
        created_at__date=today,
        status__in=['paid', 'in_progress', 'completed', 'cancelled']
    )
    
    # Calculate stats
    stats = {
        'total_orders_today': orders_today.count(),
        'total_revenue_today': OrderItem.objects.filter(order__in=orders_today).aggregate(
            total=Sum(F('quantity') * F('ice_cream__price'))
        )['total'] or 0,
        'most_popular_ice_cream': 'Vanilla',  # You can calculate this from OrderItem
        'active_tables': Table.objects.filter(
            orders__created_at__date=today,
            orders__status__in=['paid', 'in_progress', 'completed']
        ).distinct().count(),
    }
    
    # Get all recent orders (without slicing first)
    base_orders = Order.objects.filter(
        status__in=['paid', 'in_progress', 'completed', 'cancelled']
    ).select_related('table').prefetch_related('items__ice_cream').order_by('-created_at')
    
    # Group orders by status (filter before converting to list)
    orders_by_status = {
        'paid': base_orders.filter(status='paid')[:20],
        'in_progress': base_orders.filter(status='in_progress')[:20],
        'completed': base_orders.filter(status='completed')[:20],
        'cancelled': base_orders.filter(status='cancelled')[:20],
    }
    
    # Count pending orders
    pending_orders_count = Order.objects.filter(
        status__in=['paid', 'in_progress']
    ).count()
    
    # Count active tables (tables with orders today)
    active_tables_count = Table.objects.filter(
        orders__created_at__date=today,
        orders__status__in=['paid', 'in_progress', 'completed']
    ).distinct().count()
    
    context = {
        'stats': stats,
        'orders_by_status': orders_by_status,
        'pending_orders_count': pending_orders_count,
        'active_tables_count': active_tables_count,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def admin_analytics(request):
    """Advanced analytics page with day/month/year analysis"""
    from django.db.models import Count, Sum, Avg
    from datetime import datetime, timedelta
    
    # Get date range from request or default to last 30 days
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('from_date'):
        start_date = datetime.strptime(request.GET.get('from_date'), '%Y-%m-%d').date()
    if request.GET.get('to_date'):
        end_date = datetime.strptime(request.GET.get('to_date'), '%Y-%m-%d').date()
    
    # Filter orders for the date range (only paid orders)
    orders_in_range = Order.objects.filter(
        created_at__date__range=[start_date, end_date],
        status__in=['paid', 'in_progress', 'completed']
    )
    
    # Calculate analytics
    analytics = {
        'total_revenue': OrderItem.objects.filter(order__in=orders_in_range).aggregate(
            total=Sum(F('quantity') * F('ice_cream__price'))
        )['total'] or 0,
        'total_orders': orders_in_range.count(),
        'avg_order_value': orders_in_range.aggregate(
            avg=Avg('items__quantity')
        )['avg'] or 0,
        'active_tables': Table.objects.count(),
    }
    
    # Top products
    top_products = OrderItem.objects.filter(order__in=orders_in_range).values(
        'ice_cream__name'
    ).annotate(
        orders_count=Count('id'),
        revenue=Sum(F('quantity') * F('ice_cream__price'))
    ).order_by('-revenue')[:5]
    
    # Add percentage for top products
    total_revenue = analytics['total_revenue']
    for product in top_products:
        product['name'] = product['ice_cream__name']
        product['percentage'] = round((product['revenue'] / total_revenue * 100), 1) if total_revenue > 0 else 0
    
    analytics['top_products'] = top_products
    
    # Table performance
    table_performance = []
    for table in Table.objects.all():
        table_orders = orders_in_range.filter(table=table)
        table_revenue = OrderItem.objects.filter(order__in=table_orders).aggregate(
            total=Sum(F('quantity') * F('ice_cream__price'))
        )['total'] or 0
        
        table_performance.append({
            'number': table.number,
            'orders_count': table_orders.count(),
            'revenue': table_revenue,
            'percentage': round((table_revenue / total_revenue * 100), 1) if total_revenue > 0 else 0
        })
    
    table_performance.sort(key=lambda x: x['revenue'], reverse=True)
    analytics['table_performance'] = table_performance[:10]  # Top 10 tables
    
    context = {
        'analytics': analytics,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'admin_analytics.html', context)

@login_required
def admin_settings(request):
    """Admin settings page"""
    from .models import ShopSettings
    
    settings = ShopSettings.get_settings()
    
    if request.method == 'POST':
        # Handle settings save
        category = request.POST.get('category')
        
        try:
            if category == 'general':
                settings.shop_name = request.POST.get('shop_name', settings.shop_name)
                settings.currency = request.POST.get('currency', settings.currency)
                settings.timezone = request.POST.get('timezone', settings.timezone)
                settings.date_format = request.POST.get('date_format', settings.date_format)
                settings.order_prefix = request.POST.get('order_prefix', settings.order_prefix)
                settings.auto_refresh_dashboard = request.POST.get('auto_refresh') == 'on'
                
            elif category == 'shop':
                settings.shop_description = request.POST.get('shop_description', settings.shop_description)
                settings.phone = request.POST.get('phone', settings.phone)
                settings.email = request.POST.get('email', settings.email)
                settings.address = request.POST.get('address', settings.address)
                
                opening_time = request.POST.get('opening_time')
                closing_time = request.POST.get('closing_time')
                if opening_time:
                    from datetime import datetime
                    settings.opening_time = datetime.strptime(opening_time, '%H:%M').time()
                if closing_time:
                    from datetime import datetime
                    settings.closing_time = datetime.strptime(closing_time, '%H:%M').time()
                    
            elif category == 'payment':
                settings.upi_enabled = request.POST.get('upi_enabled') == 'on'
                settings.upi_id = request.POST.get('upi_id', settings.upi_id)
                settings.upi_merchant_name = request.POST.get('upi_merchant', settings.upi_merchant_name)
                
                settings.razorpay_enabled = request.POST.get('razorpay_enabled') == 'on'
                settings.razorpay_key_id = request.POST.get('razorpay_key', settings.razorpay_key_id)
                settings.razorpay_key_secret = request.POST.get('razorpay_secret', settings.razorpay_key_secret)
                
                settings.tax_rate = request.POST.get('tax_rate', settings.tax_rate)
                settings.service_charge = request.POST.get('service_charge', settings.service_charge)
                
            elif category == 'email':
                settings.smtp_host = request.POST.get('smtp_host', settings.smtp_host)
                settings.smtp_port = request.POST.get('smtp_port', settings.smtp_port)
                settings.from_email = request.POST.get('from_email', settings.from_email)
                settings.from_name = request.POST.get('from_name', settings.from_name)
                
                email_password = request.POST.get('email_password')
                if email_password:
                    settings.email_password = email_password
                    
                settings.email_verification_required = request.POST.get('email_verification') == 'on'
                
            elif category == 'notifications':
                settings.notify_new_orders = request.POST.get('notify_new_orders') == 'on'
                settings.notify_payments = request.POST.get('notify_payments') == 'on'
                settings.notify_refunds = request.POST.get('notify_refunds') == 'on'
                settings.admin_notification_email = request.POST.get('admin_email', settings.admin_notification_email)
                
                settings.daily_report_enabled = request.POST.get('daily_report') == 'on'
                report_time = request.POST.get('report_time')
                if report_time:
                    from datetime import datetime
                    settings.daily_report_time = datetime.strptime(report_time, '%H:%M').time()
                    
            elif category == 'backup':
                settings.auto_backup_enabled = request.POST.get('auto_backup') == 'on'
                backup_time = request.POST.get('backup_time')
                if backup_time:
                    from datetime import datetime
                    settings.backup_time = datetime.strptime(backup_time, '%H:%M').time()
            
            # Save settings
            settings.updated_by = request.user.username if request.user.is_authenticated else 'admin'
            settings.save()
            
            return JsonResponse({
                'success': True, 
                'message': f'{category.title()} settings saved successfully!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    context = {
        'settings': settings,
    }
    
    return render(request, 'admin_settings.html', context)

@login_required
def update_order_status(request, order_id):
    print(f"DEBUG: Update order status called - Order ID: {order_id}, Method: {request.method}")
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        old_status = order.status
        
        print(f"DEBUG: Current status: {old_status}, Requested status: {new_status}")
        
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        print(f"DEBUG: Valid statuses: {valid_statuses}")
        
        if new_status not in valid_statuses:
            print(f"DEBUG: Invalid status: {new_status}")
            return JsonResponse({'status': 'error', 'error': 'Invalid status'}, status=400)
        
        # Validation: Prevent going backwards in the order flow
        status_order = {
            'draft': 0,
            'paid': 1,
            'in_progress': 2,
            'completed': 3,
            'cancelled': 99  # Can cancel at any time
        }
        
        # Check if trying to go backwards (except for cancellation)
        if new_status != 'cancelled':
            current_level = status_order.get(old_status, 0)
            new_level = status_order.get(new_status, 0)
            
            if new_level < current_level:
                error_msg = f"Cannot change order from '{old_status}' back to '{new_status}'"
                print(f"DEBUG: {error_msg}")
                return JsonResponse({
                    'status': 'error', 
                    'error': error_msg
                }, status=400)
        
        # Additional validation: Cannot change completed orders (except to cancel)
        if old_status == 'completed' and new_status != 'cancelled':
            error_msg = "Cannot change status of completed orders. You can only cancel them."
            print(f"DEBUG: {error_msg}")
            return JsonResponse({
                'status': 'error',
                'error': error_msg
            }, status=400)
        
        # Update the status
        order.status = new_status
        order.save()
        
        # Push to Firebase
        try:
            db.reference(f'orders/{order.id}/status').set(order.get_status_display())
            print(f"Order {order.id} status updated in Firebase")
        except Exception as e:
            print(f'Firebase status update error for order {order.id}: {e}')
            # Continue without Firebase
        
        # If order is being cancelled, check if refund is needed
        if new_status == 'cancelled' and old_status != 'cancelled':
            return JsonResponse({
                'status': 'success', 
                'show_refund_popup': True,
                'order_id': order.id,
                'order_total': float(order.get_total_amount())
            })
        
        print(f"DEBUG: Order {order.id} status updated successfully from {old_status} to {new_status}")
        return JsonResponse({
            'status': 'success',
            'message': f'Order status updated to {new_status}'
        })
    
    print(f"DEBUG: Invalid request method: {request.method}")
    return JsonResponse({'status': 'error', 'error': 'Invalid request method'}, status=400)

@login_required
def order_details(request, order_id):
    """Get detailed information about an order including items"""
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Get order items with ice cream details
        items = []
        for item in order.items.all():
            items.append({
                'ice_cream_name': item.ice_cream.name,
                'quantity': item.quantity,
                'price': float(item.ice_cream.price),
                'total': float(item.quantity * item.ice_cream.price)
            })
        
        order_data = {
            'id': order.id,
            'created_at': order.created_at.strftime('%B %d, %Y at %I:%M %p'),
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'table_number': order.table.number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'payment_method': order.payment_method,
            'payment_status': order.get_payment_status_display(),
            'total_amount': float(order.get_total_amount()),
            'items': items
        }
        
        return JsonResponse({
            'success': True,
            'order': order_data
        })
        
    except Exception as e:
        print(f"Error fetching order details: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@login_required
def delete_order(request, order_id):
    """Delete an order"""
    if request.method == 'POST':
        try:
            order = get_object_or_404(Order, id=order_id)
            order_number = order.id
            
            # Delete the order (cascade will delete related items)
            order.delete()
            
            print(f"Order #{order_number} deleted successfully")
            
            return JsonResponse({
                'success': True,
                'message': f'Order #{order_number} deleted successfully'
            })
            
        except Exception as e:
            print(f"Error deleting order: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Invalid request method'
    }, status=400)

def admin_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('admin_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_login.html', {'form': form})

@login_required
def admin_logout(request):
    if request.method == 'POST':
        logout(request)
    return redirect('admin_login')

@login_required
def manage_ice_creams(request):
    from django.db.models import Count, Sum, Avg
    
    ice_creams = IceCream.objects.all()
    
    # Add statistics for each ice cream
    for ice_cream in ice_creams:
        ice_cream.total_orders = OrderItem.objects.filter(ice_cream=ice_cream).aggregate(
            total=Count('id')
        )['total'] or 0
        
        ice_cream.total_revenue = OrderItem.objects.filter(ice_cream=ice_cream).aggregate(
            total=Sum(F('quantity') * F('ice_cream__price'))
        )['total'] or 0
    
    # Calculate additional stats
    most_popular = OrderItem.objects.values('ice_cream__name').annotate(
        total=Count('id')
    ).order_by('-total').first()
    
    highest_revenue = OrderItem.objects.values('ice_cream__name').annotate(
        revenue=Sum(F('quantity') * F('ice_cream__price'))
    ).order_by('-revenue').first()
    
    average_price = IceCream.objects.aggregate(avg=Avg('price'))['avg']
    
    context = {
        'ice_creams': ice_creams,
        'most_popular': most_popular,
        'highest_revenue': highest_revenue,
        'average_price': average_price,
    }
    
    return render(request, 'manage_ice_creams.html', context)

@login_required
def add_ice_cream(request):
    if request.method == 'POST':
        form = IceCreamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_ice_creams')
    else:
        form = IceCreamForm()
    return render(request, 'ice_cream_form.html', {'form': form})

@login_required
def edit_ice_cream(request, pk):
    ice_cream = get_object_or_404(IceCream, pk=pk)
    if request.method == 'POST':
        form = IceCreamForm(request.POST, request.FILES, instance=ice_cream)
        if form.is_valid():
            form.save()
            return redirect('manage_ice_creams')
    else:
        form = IceCreamForm(instance=ice_cream)
    return render(request, 'ice_cream_form.html', {'form': form})

@login_required
def delete_ice_cream(request, pk):
    ice_cream = get_object_or_404(IceCream, pk=pk)
    ice_cream.delete()
    return redirect('manage_ice_creams')

@login_required
def manage_tables(request):
    from django.db.models import Count, Sum
    
    tables = Table.objects.all()
    
    # Add statistics for each table
    for table in tables:
        today_orders = Order.objects.filter(
            table=table,
            created_at__date=timezone.now().date(),
            status__in=['paid', 'in_progress', 'completed']
        )
        table.orders_today = today_orders.count()
        
        table.revenue_today = OrderItem.objects.filter(
            order__in=today_orders
        ).aggregate(
            total=Sum(F('quantity') * F('ice_cream__price'))
        )['total'] or 0
    
    # Calculate additional stats
    most_active_table = None
    if tables:
        table_orders = []
        for table in tables:
            orders_count = Order.objects.filter(
                table=table,
                status__in=['paid', 'in_progress', 'completed']
            ).count()
            table_orders.append((table.number, orders_count))
        
        if table_orders:
            most_active_table = max(table_orders, key=lambda x: x[1])[0]
    
    avg_orders_per_table = Order.objects.filter(
        status__in=['paid', 'in_progress', 'completed']
    ).count() / tables.count() if tables.count() > 0 else 0
    
    total_capacity = sum(getattr(table, 'seats', 4) for table in tables)
    
    context = {
        'tables': tables,
        'most_active_table': most_active_table,
        'avg_orders_per_table': avg_orders_per_table,
        'total_capacity': total_capacity,
    }
    
    return render(request, 'manage_tables.html', context)

@login_required
def add_table(request):
    if request.method == 'POST':
        print(f"POST data received: {request.POST}")  # Debug log
        
        # Handle form data manually for better control
        number = request.POST.get('number')
        seats = request.POST.get('seats', 4)
        description = request.POST.get('description', '')
        
        print(f"Parsed data - Number: {number}, Seats: {seats}, Description: {description}")  # Debug log
        
        try:
            # Validate number
            if not number:
                messages.error(request, 'Table number is required!')
                return render(request, 'add_table.html')
            
            # Check if table number already exists
            if Table.objects.filter(number=number).exists():
                messages.error(request, f'Table {number} already exists!')
                return render(request, 'add_table.html')
            
            # Create new table
            table = Table.objects.create(
                number=int(number),
                seats=int(seats),
                description=description
            )
            
            print(f"Table created successfully: {table}")  # Debug log
            messages.success(request, f'Table {number} created successfully!')
            return redirect('manage_tables')
            
        except ValueError as e:
            messages.error(request, f'Invalid number format: {str(e)}')
            return render(request, 'add_table.html')
        except Exception as e:
            print(f"Error creating table: {e}")  # Debug log
            messages.error(request, f'Error creating table: {str(e)}')
            return render(request, 'add_table.html')
    
    return render(request, 'add_table.html')

@login_required
def edit_table(request, pk):
    table = get_object_or_404(Table, pk=pk)
    
    if request.method == 'POST':
        # Handle form data manually for better control
        number = request.POST.get('number')
        seats = request.POST.get('seats', 4)
        description = request.POST.get('description', '')
        
        try:
            # Check if table number already exists (excluding current table)
            if Table.objects.filter(number=number).exclude(pk=pk).exists():
                messages.error(request, f'Table {number} already exists!')
                return render(request, 'edit_table.html', {'table': table})
            
            # Update table
            table.number = number
            table.seats = int(seats)
            table.description = description
            table.save()
            
            messages.success(request, f'Table {number} updated successfully!')
            return redirect('manage_tables')
            
        except Exception as e:
            messages.error(request, f'Error updating table: {str(e)}')
            return render(request, 'edit_table.html', {'table': table})
    
    # Add statistics for the table
    from django.db.models import Count, Sum
    
    table.total_orders = Order.objects.filter(
        table=table,
        status__in=['paid', 'in_progress', 'completed']
    ).count()
    
    table.total_revenue = OrderItem.objects.filter(
        order__table=table,
        order__status__in=['paid', 'in_progress', 'completed']
    ).aggregate(
        total=Sum(F('quantity') * F('ice_cream__price'))
    )['total'] or 0
    
    table.orders_today = Order.objects.filter(
        table=table,
        created_at__date=timezone.now().date(),
        status__in=['paid', 'in_progress', 'completed']
    ).count()
    
    table.avg_order = table.total_revenue / table.total_orders if table.total_orders > 0 else 0
    
    return render(request, 'edit_table.html', {'table': table})

@login_required
def delete_table(request, pk):
    table = get_object_or_404(Table, pk=pk)
    table.delete()
    return redirect('manage_tables')

@login_required
def clear_all_orders(request):
    if request.method == 'POST':
        Order.objects.all().delete()
        # Also clear Firebase orders
        try:
            db.reference('orders').delete()
        except Exception as e:
            print(f'Firebase clear_all_orders error: {e}')
        return JsonResponse({'status': 'success', 'message': 'All orders cleared successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def delete_order(request, order_id):
    if request.method == 'POST':
        try:
            order = Order.objects.get(id=order_id)
            order.delete()
            # Also delete from Firebase if exists
            try:
                db.reference(f'orders/{order_id}').delete()
            except Exception as e:
                print(f'Firebase delete_order error for {order_id}: {e}')
            return JsonResponse({'status': 'success', 'message': 'Order deleted successfully'})
        except Order.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Order not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def order_success(request):
    from django.utils import timezone
    order_id = request.GET.get('order_id')
    order = None
    items = []
    total = 0
    can_order_again = True
    cooldown_seconds = 120  # 2 minutes
    cooldown_remaining = 0

    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            items = order.items.select_related('ice_cream').all()
            total = order.get_total_amount()
        except Order.DoesNotExist:
            order = None

    # Restrict re-ordering for 2 minutes using session
    last_order_time = request.session.get('last_order_time')
    now = timezone.now().timestamp()
    if last_order_time:
        elapsed = now - last_order_time
        if elapsed < cooldown_seconds:
            can_order_again = False
            cooldown_remaining = int(cooldown_seconds - elapsed)
    # Set last_order_time for this order
    request.session['last_order_time'] = now

    return render(request, 'order_success.html', {
        'order_id': order_id,
        'order': order,
        'items': items,
        'total': total,
        'can_order_again': can_order_again,
        'cooldown_remaining': cooldown_remaining,
    })

@login_required
def process_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Use customer details from the order (not session)
        customer_email = order.customer_email
        customer_name = order.customer_name
        
        # Create refund with actual customer data from order
        refund = Refund.objects.create(
            order=order,
            customer_email=customer_email,
            customer_name=customer_name,
            refund_amount=order.get_total_amount(),
            payment_method='bank_transfer',  # Default to bank transfer
            payment_details='Refund will be processed to your original payment method',
            refund_reason='Item not available',
            status='pending'
        )
        
        # Send refund email to customer
        try:
            send_refund_email(refund)
            return JsonResponse({
                'status': 'success', 
                'message': 'Refund processed and email sent to customer'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'success', 
                'message': f'Refund processed but email failed: {str(e)}'
            })
    
    # For GET request, return form data with actual customer details from order
    customer_email = order.customer_email
    customer_name = order.customer_name
    
    form = RefundForm(initial={
        'refund_amount': order.get_total_amount(),
        'customer_email': customer_email,
        'customer_name': customer_name,
    })
    
    return JsonResponse({
        'status': 'success',
        'form_html': render_to_string('refund_form.html', {
            'form': form,
            'order': order,
            'customer_email': customer_email,
            'customer_name': customer_name,
        }, request=request)
    })

def send_refund_email(refund):
    """Send refund notification email to customer"""
    subject = f'Refund Processed - Order #{refund.order.id}'
    
    # Render HTML email template
    html_message = render_to_string('emails/refund_notification.html', {
        'refund': refund,
        'order': refund.order,
    })
    
    # Create plain text version
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[refund.customer_email],
        html_message=html_message,
        fail_silently=False,
    )

@login_required
def refund_list(request):
    """View to list all refunds"""
    from django.db.models import Count, Sum
    
    refunds = Refund.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    status_filter = request.GET.get('status')
    date_filter = request.GET.get('date')
    
    if status_filter:
        refunds = refunds.filter(status=status_filter)
    
    if date_filter:
        refunds = refunds.filter(created_at__date=date_filter)
    
    # Calculate statistics
    pending_count = refunds.filter(status='pending').count()
    processed_count = refunds.filter(status='processed').count()
    total_refund_amount = refunds.aggregate(
        total=Sum('refund_amount')
    )['total'] or 0
    
    context = {
        'refunds': refunds,
        'pending_count': pending_count,
        'processed_count': processed_count,
        'total_refund_amount': total_refund_amount,
    }
    
    return render(request, 'refund_list.html', context)

@login_required
def update_refund_status(request, refund_id):
    """Update refund status"""
    if request.method == 'POST':
        refund = get_object_or_404(Refund, id=refund_id)
        status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        
        if status in [s[0] for s in Refund.REFUND_STATUS_CHOICES]:
            refund.status = status
            refund.admin_notes = admin_notes
            if status == 'processed':
                refund.processed_at = timezone.now()
            refund.save()
            
            return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_orders_json(request):
    """Get orders as JSON for real-time updates"""
    orders = Order.objects.all().order_by('-created_at')[:20]  # Latest 20 orders
    
    orders_data = []
    for order in orders:
        orders_data.append({
            'id': order.id,
            'customer_name': order.customer_name,
            'customer_email': order.customer_email,
            'table_number': order.table.number,
            'status': order.status,
            'payment_status': order.payment_status,
            'total_amount': float(order.get_total_amount()),
            'created_at': order.created_at.isoformat(),
            'items': [
                {
                    'name': item.ice_cream.name,
                    'quantity': item.quantity,
                    'price': float(item.ice_cream.price)
                }
                for item in order.items.all()
            ]
        })
    
    return JsonResponse({
        'status': 'success',
        'orders': orders_data,
        'count': len(orders_data)
    })

@login_required
def admin_dashboard_simple(request):
    """Simple dashboard for debugging"""
    today = timezone.now().date()
    orders_today = Order.objects.filter(created_at__date=today)
    
    stats = {
        'total_orders_today': orders_today.count(),
        'total_revenue_today': OrderItem.objects.filter(order__in=orders_today).aggregate(
            total=Sum(F('quantity') * F('ice_cream__price'))
        )['total'] or 0,
    }

    most_popular_item = OrderItem.objects.values('ice_cream__name').annotate(
        total=Count('id')
    ).order_by('-total').first()
    stats['most_popular_ice_cream'] = most_popular_item['ice_cream__name'] if most_popular_item else 'N/A'
    
    all_orders = Order.objects.all().order_by('-created_at')
    orders_by_status = {
        'pending': all_orders.filter(status__in=['pending', 'pending_payment']),
        'in_progress': all_orders.filter(status__in=['in_progress', 'paid']),
        'completed': all_orders.filter(status='completed'),
        'cancelled': all_orders.filter(status='cancelled'),
    }

    context = {
        'stats': stats,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'admin_dashboard.html', context)