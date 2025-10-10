# Ice Cream QR Ordering System

A modern, full-featured QR code-based ordering system for ice cream shops with real-time admin dashboard, email verification, and payment integration.

## Features

### Customer Features
- **QR Code Ordering** - Scan table QR codes to place orders
- **Email Verification** - Secure email-based customer verification
- **AI Recommendations** - Smart ice cream suggestions based on preferences
- **Real-time Cart** - Dynamic cart with live total calculations
- **Multiple Payment Options** - UPI and Razorpay integration
- **Order Tracking** - Real-time order status updates
- **Mobile Responsive** - Optimized for all devices

### Admin Features
- **Modern Dashboard** - Real-time statistics and order management
- **Advanced Analytics** - Day/month/year sales analysis with charts
- **Ice Cream Management** - Add, edit, delete flavors with statistics
- **Table Management** - QR code generation and table performance tracking
- **Refund Management** - Process customer refunds with email notifications
- **Settings Panel** - Comprehensive configuration management
- **Email System** - Automated notifications and confirmations

### Technical Features
- **Django Backend** - Robust Python web framework
- **Firebase Integration** - Real-time database synchronization
- **Gmail SMTP** - Professional email delivery
- **Chart.js Analytics** - Interactive data visualizations
- **Tailwind CSS** - Modern, responsive design
- **Mobile-First** - Optimized for mobile devices

## Quick Start

### Prerequisites
- Python 3.8+
- Django 4.0+
- Gmail account for SMTP
- Firebase project (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vikashere96/ice-cream-app.git
   cd ice-cream-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

## Configuration

### Email Settings
Configure Gmail SMTP in `.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Payment Settings
Configure payment gateways in admin settings:
- **UPI**: Set your UPI ID in admin panel
- **Razorpay**: Add API keys in settings

### Firebase (Optional)
For real-time features, add Firebase configuration:
```env
FIREBASE_CONFIG=path/to/firebase-service-account-key.json
```

## Usage

### For Customers
1. **Scan QR Code** - Use phone camera to scan table QR code
2. **Email Verification** - Enter email and verify with 6-digit code
3. **Browse Menu** - View ice cream flavors with AI recommendations
4. **Place Order** - Add items to cart and complete payment
5. **Track Order** - Monitor order status in real-time

### For Admins
1. **Access Admin Panel** - Visit `/panel/login/`
2. **Dashboard** - View real-time statistics and manage orders
3. **Analytics** - Analyze sales data with interactive charts
4. **Management** - Manage ice creams, tables, and refunds
5. **Settings** - Configure shop information and payment methods

## Project Structure

```
ice-cream-app/
├── icecream_qr/          # Django project settings
├── qr_ordering/          # Main application
│   ├── models.py         # Database models
│   ├── views.py          # Business logic
│   ├── urls.py           # URL routing
│   ├── templates/        # HTML templates
│   └── static/           # CSS, JS, images
├── media/                # User uploads
├── static/               # Static files
├── requirements.txt      # Python dependencies
├── manage.py            # Django management
└── README.md            # This file
```

## Security Features

- **Email Verification** - Prevents spam orders
- **CSRF Protection** - Secure form submissions
- **Rate Limiting** - Prevents abuse
- **Input Validation** - Sanitized user inputs
- **Secure Payments** - Encrypted payment processing

## Deployment

### Production Setup
1. **Environment Variables** - Set production values in `.env`
2. **Static Files** - Run `python manage.py collectstatic`
3. **Database** - Use PostgreSQL for production
4. **Web Server** - Deploy with Gunicorn + Nginx
5. **SSL Certificate** - Enable HTTPS for security

### Recommended Hosting
- **Heroku** - Easy deployment with add-ons
- **DigitalOcean** - VPS with full control
- **AWS** - Scalable cloud infrastructure
- **Railway** - Modern deployment platform

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Django** - Web framework
- **Tailwind CSS** - Styling framework
- **Chart.js** - Data visualization
- **Firebase** - Real-time database
- **Font Awesome** - Icons

## Support

For support and questions:
- **GitHub Issues** - Report bugs and feature requests
- **Email** - Contact the development team
- **Documentation** - Check the wiki for detailed guides

---

**Built with love for ice cream lovers everywhere!**