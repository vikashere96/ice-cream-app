# 🍦 Ice Cream QR Ordering System

A complete Django-based QR code ordering system for ice cream shops with admin panel, payment integration, and real-time order management.

## ✨ Features

### Customer Features
- 📱 **QR Code Ordering** - Scan table QR code to order
- 📧 **Email Verification** - Secure customer authentication
- 🍨 **Interactive Menu** - Browse ice cream flavors with images
- 💳 **Multiple Payment Options** - UPI and Razorpay integration
- 📊 **Order Tracking** - Real-time order status updates
- 📱 **Mobile Optimized** - Perfect mobile experience

### Admin Features
- 📊 **Dashboard** - Real-time statistics and order management
- 🍦 **Ice Cream Management** - Add, edit, delete products
- 🪑 **Table Management** - QR code generation for tables
- 📦 **Order Management** - Update status, view details, delete orders
- 💰 **Payment Tracking** - Monitor revenue and transactions
- ⚙️ **Settings** - Configure shop details, payments, email
- 📈 **Analytics** - Sales reports and insights

## 🚀 Quick Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/vikashere96/ice-cream-app.git
cd ice-cream-app
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Copy the example file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env file with your settings
```

**Required Configuration:**
- `EMAIL_HOST_USER` - Your Gmail address
- `EMAIL_HOST_PASSWORD` - Gmail App Password (see below)
- `UPI_MERCHANT_ID` - Your UPI ID
- `SECRET_KEY` - Django secret key (generate new one)

**Generate Gmail App Password:**
1. Go to https://myaccount.google.com/apppasswords
2. Select "Mail" and "Other (Custom name)"
3. Name it "Ice Cream Shop"
4. Copy the 16-character password
5. Paste in `.env` file (remove spaces)

#### 5. Setup Database
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 6. Create Admin User
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

#### 7. Add Firebase Configuration (Optional)
- Place your `firebase-service-account-key.json` in the project root
- Or skip this step (app will work without Firebase)

#### 8. Run the Server
```bash
python manage.py runserver
```

#### 9. Access the Application
- **Customer Order Page**: http://127.0.0.1:8000/order/table/1/
- **Admin Panel**: http://127.0.0.1:8000/panel/login/
- **Admin Dashboard**: http://127.0.0.1:8000/panel/dashboard/

## 📋 Initial Setup Tasks

### 1. Add Ice Cream Products
1. Login to admin panel
2. Go to "Ice Creams" section
3. Click "Add Ice Cream"
4. Fill in name, price, and upload image
5. Save

### 2. Create Tables
1. Go to "Tables" section
2. Click "Add Table"
3. Enter table number and seats
4. QR code will be generated automatically
5. Print QR code for the table

### 3. Configure Settings
1. Go to "Settings" section
2. Update shop information
3. Configure payment methods
4. Set up email notifications
5. Save changes

## 🔧 Configuration

### Email Setup (Gmail)

1. **Enable 2-Step Verification**
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Go to https://myaccount.google.com/apppasswords
   - Create password for "Mail"
   - Copy and paste in `.env`

3. **Update .env**
   ```env
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   ```

### Payment Setup

#### UPI Payment
```env
UPI_MERCHANT_ID=your-upi-id@bank
UPI_MERCHANT_NAME=Your Shop Name
```

#### Razorpay (Optional)
1. Sign up at https://razorpay.com
2. Get API keys from dashboard
3. Update `.env`:
   ```env
   RAZORPAY_KEY_ID=rzp_test_xxxxx
   RAZORPAY_KEY_SECRET=your_secret_key
   ```

## 📱 Using the System

### For Customers

1. **Scan QR Code** - Use phone camera to scan table QR
2. **Browse Menu** - View available ice cream flavors
3. **Add to Cart** - Select items and quantities
4. **Enter Email** - Provide email for verification
5. **Verify Email** - Enter 6-digit code (or use 123456 for testing)
6. **Choose Payment** - Select UPI or Razorpay
7. **Complete Payment** - Follow payment instructions
8. **Order Confirmed** - Receive confirmation email

### For Admin

1. **Login** - Access admin panel
2. **View Dashboard** - See real-time orders and stats
3. **Manage Orders** - Update status (Paid → In Progress → Completed)
4. **Delete Orders** - Remove unwanted orders
5. **Manage Products** - Add/edit ice cream items
6. **Manage Tables** - Create tables and QR codes
7. **View Analytics** - Check sales reports

### Screenshots
media/ss/dashboard.png
media/ss/Icecream.png
media/ss/login.png
media/ss/qr.png
media/ss/cust.png
media/ss/cust1.png
media/ss/cust2.png


## 🎯 Order Status Flow

```
Paid → In Progress → Completed
  ↓         ↓            ↓
Cancelled  Cancelled  Cancelled
```

**Rules:**
- ✅ Can only move forward
- ✅ Can cancel at any stage
- ❌ Cannot go backwards
- ❌ Cannot change completed orders (except cancel)

## 🗂️ Project Structure

```
ice-cream-app/
├── icecream_qr/          # Django project settings
│   ├── settings.py       # Main settings
│   ├── urls.py          # Root URL configuration
│   └── wsgi.py          # WSGI configuration
├── qr_ordering/          # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View functions
│   ├── urls.py          # App URL routing
│   ├── forms.py         # Django forms
│   ├── templates/       # HTML templates
│   └── migrations/      # Database migrations
├── media/               # Uploaded files
│   ├── ice_cream_images/  # Product images
│   └── qr_codes/        # Generated QR codes
├── static/              # Static files (CSS, JS)
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment file
├── .gitignore          # Git ignore rules
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

## 🔒 Security Notes

1. **Never commit `.env` file** - Contains sensitive data
2. **Use App Passwords** - Not regular Gmail password
3. **Change SECRET_KEY** - Generate new one for production
4. **Set DEBUG=False** - In production environment
5. **Use HTTPS** - Enable secure cookies in production

## 🐛 Troubleshooting

### Email Not Sending
- Check Gmail App Password is correct
- Verify 2-Step Verification is enabled
- Remove spaces from App Password
- Check EMAIL_HOST_USER matches Gmail account

### Orders Not Showing
- Refresh dashboard (Ctrl+F5)
- Check order status (only paid/in_progress/completed/cancelled show)
- Verify database migrations are applied

### QR Code Not Working
- Check table exists in database
- Verify QR code URL is correct
- Test with different QR scanner app

### Payment Issues
- Verify UPI ID is correct
- Check Razorpay keys are valid
- Test with small amount first

## 📚 API Endpoints

### Customer Endpoints
- `GET /order/table/<id>/` - Order page for table
- `POST /customer/verify-email/` - Verify email code
- `POST /customer/resend-verification/` - Resend code
- `POST /order/create/` - Create new order

### Admin Endpoints
- `GET /panel/login/` - Admin login
- `GET /panel/dashboard/` - Admin dashboard
- `GET /panel/ice-creams/` - Manage ice creams
- `GET /panel/tables/` - Manage tables
- `POST /panel/order/<id>/update/` - Update order status
- `POST /panel/order/<id>/delete/` - Delete order
- `GET /panel/settings/` - Shop settings

## 🔄 Updating the Project

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Restart server
python manage.py runserver
```

## 📦 Dependencies

Main packages:
- Django 5.1.6 - Web framework
- Pillow - Image processing
- qrcode - QR code generation
- firebase-admin - Firebase integration (optional)
- python-dotenv - Environment variables

See `requirements.txt` for complete list.

## 🤝 Contributing

This is a private repository. For access or contributions, contact the repository owner.

## 📄 License

Private project - All rights reserved.

## 👨‍💻 Author

**Vikas Thakor**
- GitHub: [@vikashere96](https://github.com/vikashere96)
- Email: vikasmca96@gmail.com

## 🆘 Support

For issues or questions:
1. Check troubleshooting section above
2. Review error messages in terminal
3. Check Django logs
4. Contact repository owner

## 🎉 Acknowledgments

Built with:
- Django - Web framework
- Tailwind CSS - Styling
- Chart.js - Analytics charts
- Font Awesome - Icons
- Firebase - Real-time updates (optional)

---

**Made with ❤️ for ice cream shops**

Last Updated: November 2025
