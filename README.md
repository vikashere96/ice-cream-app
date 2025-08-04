# Ice Cream QR Ordering System

## Project Overview

This project is a QR-based digital ordering system for ice cream parlors, built with Django. It allows customers to scan a QR code at their table, view the menu, and place orders directly from their mobile devices. The system features a real-time admin dashboard for managing orders, tables, and menu items, and integrates with Firebase for live order updates.

### Key Features

- **QR Code Table Ordering:** Each table has a unique QR code. Scanning it opens a web page for that table, allowing customers to order ice cream.
- **Dynamic Menu:** Customers can view available ice creams, including images and prices, and select quantities.
- **Order Management:** Orders are tracked by table and status (Pending, In Progress, Completed, Cancelled).
- **Admin Dashboard:** Staff can log in to view, update, and manage all orders, tables, and menu items.
- **Real-Time Updates:** Order status changes are pushed to Firebase for instant updates.
- **Table & Menu Management:** Admins can add, edit, or remove tables and ice cream menu items.
- **QR Code Generation:** QR codes are automatically generated for each table and link to the ordering page.

### Design & Animation

- **Modern UI:** The frontend uses Tailwind CSS for a clean, responsive, and modern look.
- **Order Cards:** Orders are displayed as animated cards with color-coded status badges.
- **Smooth Transitions:** UI elements such as modals, dropdowns, and status changes use smooth CSS transitions for a polished user experience.
- **Mobile-First:** The ordering page is optimized for mobile devices, ensuring a seamless experience for customers.

---

## Setup Process

### 1. Clone the Repository

```bash
git clone https://github.com/vikashere96/ice-cream-app.git
cd ice-cream-app
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** If `requirements.txt` is missing, install Django and Firebase Admin SDK:
> ```
> pip install django firebase-admin qrcode pillow
> ```

### 4. Firebase Setup

- Place your `firebase-service-account-key.json` in the project root.
- Make sure your Firebase Realtime Database is set up and the credentials file is correct.

### 5. Database Migration

```bash
python manage.py migrate
```

### 6. Seed Initial Data (Optional)

To add sample ice creams and tables:

```bash
python manage.py seed_data
```

### 7. Create a Superuser (for admin access)

```bash
python manage.py createsuperuser
```

### 8. Run the Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

- Access the app at `http://localhost:8000/` or your server’s IP.

---

## Usage

- **Customer:** Scan the QR code at your table, select ice creams, and place your order.
- **Admin:** Log in at `/panel/login/` to manage orders, tables, and menu items.

---

## Folder Structure

- `icecream_qr/` – Django project settings
- `qr_ordering/` – Main app (models, views, templates)
- `media/` – Uploaded images and generated QR codes
- `static/` – Static files (CSS, JS)
- `firebase-service-account-key.json` – Firebase credentials

---

## Customization

- **Design:** Modify templates in `qr_ordering/templates/` and styles in `static/`.
- **Animations:** Enhance UI/UX with additional CSS or JS as needed.

---

## License

MIT License