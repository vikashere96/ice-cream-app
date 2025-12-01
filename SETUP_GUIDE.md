# 🚀 Ice Cream App - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [First Run](#first-run)
5. [Initial Setup](#initial-setup)
6. [Testing](#testing)
7. [Deployment](#deployment)

---

## Prerequisites

### Required Software
- ✅ Python 3.8 or higher
- ✅ pip (Python package manager)
- ✅ Git

### Check Your Installation
```bash
python --version    # Should show 3.8+
pip --version      # Should show pip version
git --version      # Should show git version
```

---

## Installation

### Step 1: Clone Repository
```bash
# Clone the repository
git clone https://github.com/vikashere96/ice-cream-app.git

# Navigate to project folder
cd ice-cream-app
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install all required packages (Django, Pillow, etc.)

---

## Configuration

### Step 1: Create Environment File

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

### Step 2: Edit .env File

Open `.env` in a text editor and update:

#### Email Configuration
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password-here
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**How to get Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. You may need to enable 2-Step Verification first
3. Select "Mail" and "Other (Custom name)"
4. Name it "Ice Cream Shop"
5. Click "Generate"
6. Copy the 16-character password (remove spaces)
7. Paste in `.env` file

#### Payment Configuration
```env
UPI_MERCHANT_ID=your-upi-id@bank
UPI_MERCHANT_NAME=Your Shop Name
```

#### Django Secret Key
```bash
# Generate a new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Copy the output and paste in `.env`:
```env
SECRET_KEY=your-generated-secret-key-here
```

### Step 3: Firebase (Optional)

If you have Firebase:
1. Download `firebase-service-account-key.json`
2. Place it in project root folder
3. If you don't have it, the app will work without Firebase

---

## First Run

### Step 1: Setup Database
```bash
# Create database tables
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Create Admin User
```bash
python manage.py createsuperuser
```

Enter:
- Username: `admin` (or your choice)
- Email: your email
- Password: create a strong password
- Confirm password

### Step 3: Start Server
```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### Step 4: Test Access

Open browser and visit:
- **Admin Login**: http://127.0.0.1:8000/panel/login/
- Login with your admin credentials

---

## Initial Setup

### 1. Add Ice Cream Products

1. Go to http://127.0.0.1:8000/panel/ice-creams/
2. Click "Add Ice Cream"
3. Fill in:
   - Name: e.g., "Vanilla Supreme"
   - Price: e.g., 50
   - Image: Upload a nice ice cream image
4. Click "Create Ice Cream"
5. Repeat for more flavors

**Suggested Products:**
- Vanilla - ₹50
- Chocolate - ₹55
- Strawberry - ₹60
- Mango - ₹45
- Butterscotch - ₹65

### 2. Create Tables

1. Go to http://127.0.0.1:8000/panel/tables/
2. Click "Add Table"
3. Fill in:
   - Table Number: 1
   - Seats: 4
   - Description: "Near window"
4. Click "Create Table"
5. QR code will be generated automatically
6. Repeat for more tables

### 3. Configure Settings

1. Go to http://127.0.0.1:8000/panel/settings/
2. Update:
   - **General**: Shop name, currency
   - **Shop Info**: Phone, email, address, hours
   - **Payment**: Verify UPI settings
   - **Email**: Verify SMTP settings
3. Click "Save Changes" for each section

---

## Testing

### Test Customer Flow

1. **Access Order Page**
   ```
   http://127.0.0.1:8000/order/table/1/
   ```

2. **Place Test Order**
   - Add items to cart
   - Enter email address
   - Use verification code: `123456` (development mode)
   - Choose payment method
   - Complete order

3. **Check Dashboard**
   ```
   http://127.0.0.1:8000/panel/dashboard/
   ```
   - Order should appear in "PAID" section

### Test Admin Functions

1. **Update Order Status**
   - Click play button (▶️) to start preparing
   - Click check button (✅) to mark complete

2. **View Order Details**
   - Click "View Details" on any order
   - Check items and customer info

3. **Delete Order**
   - Click trash button (🗑️)
   - Confirm deletion

---

## Deployment

### For Production

1. **Update .env**
   ```env
   DEBUG=False
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Use Production Server**
   - Use Gunicorn, uWSGI, or similar
   - Set up Nginx/Apache
   - Use PostgreSQL instead of SQLite

### Using ngrok (for testing)

1. **Install ngrok**
   - Download from https://ngrok.com/

2. **Run ngrok**
   ```bash
   ngrok http 8000
   ```

3. **Update Django Settings**
   - Add ngrok URL to `ALLOWED_HOSTS` in settings.py

4. **Access via ngrok URL**
   - Use the https URL provided by ngrok

---

## Common Issues & Solutions

### Issue: Email not sending
**Solution:**
- Verify Gmail App Password is correct
- Check 2-Step Verification is enabled
- Remove spaces from password
- Use development code `123456` for testing

### Issue: Orders not showing in dashboard
**Solution:**
- Refresh page (Ctrl+F5)
- Check order status (only paid/in_progress/completed show)
- Verify migrations are applied

### Issue: QR code not working
**Solution:**
- Check table exists in database
- Verify URL in QR code
- Test with different QR scanner

### Issue: Images not displaying
**Solution:**
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings
- Verify images are uploaded to `media/` folder
- Check file permissions

---

## Quick Reference

### Start Server
```bash
# Activate virtual environment first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run server
python manage.py runserver
```

### Stop Server
Press `Ctrl+C` in terminal

### Access Points
- Customer Order: http://127.0.0.1:8000/order/table/1/
- Admin Login: http://127.0.0.1:8000/panel/login/
- Admin Dashboard: http://127.0.0.1:8000/panel/dashboard/

### Development Code
- Email Verification: `123456`

---

## Next Steps

1. ✅ Complete initial setup
2. ✅ Add products and tables
3. ✅ Test order flow
4. ✅ Configure settings
5. ✅ Print QR codes for tables
6. ✅ Train staff on admin panel
7. ✅ Go live!

---

## Support

For help:
1. Check this guide
2. Review README.md
3. Check error messages in terminal
4. Contact: vikasmca96@gmail.com

---

**Happy Selling! 🍦**
