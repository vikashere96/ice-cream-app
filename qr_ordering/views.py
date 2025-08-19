# qr_ordering/views.py

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, get_object_or_404, redirect
from .models import IceCream, Table, Order, OrderItem
from .forms import IceCreamForm, TableForm
from django.http import JsonResponse
import json
from django.contrib.auth.decorators import login_required
from firebase_admin import db
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Sum, F


def order_page(request, token):
    table = get_object_or_404(Table, token=token)
    ice_creams = IceCream.objects.all()
    customer_name = request.session.get('customer_name')
    customer_picture = request.session.get('customer_picture')
    return render(request, 'order_page.html', {
        'table': table,
        'ice_creams': ice_creams,
        'customer_name': customer_name,
        'customer_picture': customer_picture,
    })
from django.views.decorators.csrf import csrf_exempt
import requests
# Google login endpoint for customer
@csrf_exempt
def customer_google_login(request):
    import json
    if request.method == 'POST':
        data = json.loads(request.body)
        token = data.get('credential')
        # Verify token with Google
        google_response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
        if google_response.status_code == 200:
            info = google_response.json()
            name = info.get('name')
            picture = info.get('picture')
            email = info.get('email')
            # Store in session
            request.session['customer_name'] = name
            request.session['customer_picture'] = picture
            request.session['customer_email'] = email
            return JsonResponse({'success': True, 'name': name, 'picture': picture, 'email': email})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid token'}, status=400)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def submit_order(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_id = data['table_id']
        items = data['items']

        table = get_object_or_404(Table, id=table_id)
        
        order = Order.objects.create(table=table)
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
            'status': order.get_status_display(),
            'created_at': order.created_at.isoformat(),
            'items': [{'quantity': item.quantity, 'name': item.ice_cream.name} for item in order.items.all()]
        }
        status_url = reverse('order_status', kwargs={'order_id': order.id})
        try:
            db.reference(f'orders/{order.id}').set(order_data)
            print(f"Order {order.id} synced to Firebase successfully")
        except Exception as e:
            print(f'Firebase error for order {order.id}: {e}')
            # Continue without Firebase - order is still saved in Django database
            return JsonResponse({'status': 'success', 'order_id': order.id, 'status_url': status_url})
        
        return JsonResponse({'status': 'success', 'order_id': order.id, 'status_url': status_url})
    return JsonResponse({'status': 'error'}, status=400)

def order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_status.html', {'order': order})

@login_required
def admin_dashboard(request):
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
        'pending': all_orders.filter(status='pending'),
        'in_progress': all_orders.filter(status='in_progress'),
        'completed': all_orders.filter(status='completed'),
        'cancelled': all_orders.filter(status='cancelled'),
    }

    context = {
        'stats': stats,
        'orders_by_status': orders_by_status,
    }
    
    return render(request, 'admin_dashboard.html', context)

@login_required
def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        status = request.POST.get('status')
        if status in [s[0] for s in Order.STATUS_CHOICES]:
            order.status = status
            order.save()
            
            # Push to Firebase
            try:
                db.reference(f'orders/{order.id}/status').set(order.get_status_display())
                print(f"Order {order.id} status updated in Firebase")
            except Exception as e:
                print(f'Firebase status update error for order {order.id}: {e}')
                # Continue without Firebase
            
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

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
    ice_creams = IceCream.objects.all()
    return render(request, 'manage_ice_creams.html', {'ice_creams': ice_creams})

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
    tables = Table.objects.all()
    return render(request, 'manage_tables.html', {'tables': tables})

@login_required
def add_table(request):
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_tables')
    else:
        form = TableForm()
    return render(request, 'table_form.html', {'form': form})

@login_required
def edit_table(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('manage_tables')
    else:
        form = TableForm(instance=table)
    return render(request, 'table_form.html', {'form': form})

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
