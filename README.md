# AskSanatan – Online Pooja Samagri & Spiritual Services E-Commerce Platform

BCA Major Project | Flask + SQLite + Bootstrap 5

## Project Structure

```
asksanatan/
├── app.py                 # Application factory
├── run.py                 # Entry point
├── config.py              # Configuration
├── extensions.py          # DB & Login extensions
├── models.py              # SQLAlchemy models
├── forms.py               # WTForms validation
├── utils.py               # Helpers & seed data
├── requirements.txt
├── .env                   # Environment variables (admin credentials)
├── .env.example
├── routes/
│   ├── main.py            # Home, About, Contact
│   ├── auth.py            # Register, Login, Profile
│   ├── shop.py            # Products, Orders, Dashboard
│   ├── cart.py            # Cart & Checkout
│   └── admin.py           # Admin panel
├── static/
│   ├── css/style.css
│   └── js/main.js
└── templates/
    ├── base.html
    ├── home.html, about.html, contact.html
    ├── auth/, shop/, admin/, errors/
```

## Installation (VS Code)

```bash
cd asksanatan
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # Edit admin credentials if needed
python3 run.py
```

Open: **http://127.0.0.1:5001** (port 5001 avoids macOS AirPlay conflict on 5000)

## Default Admin Login (from `.env`)

| Field    | Value                  |
|----------|------------------------|
| Email    | admin@asksanatan.com   |
| Password | Admin@12345            |

Change credentials in `.env`:

```
ADMIN_NAME=Admin
ADMIN_EMAIL=admin@asksanatan.com
ADMIN_PASSWORD=YourSecurePassword
```

## Database

- SQLite file: `instance/asksanatan.db` (auto-created on first run)
- Tables: users, categories, products, cart_items, orders, order_items
- Sample products & categories seeded automatically

## Features

**Customer:** Register, Login, Browse/Search/Filter products, Cart, Checkout, Order history, Profile

**Admin:** Dashboard, CRUD products, Categories, Users list, Order management, Chart.js analytics

## Tech Stack

Flask, SQLAlchemy, Flask-Login, Flask-WTF, SQLite, Bootstrap 5, Chart.js
