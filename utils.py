"""Utility helpers."""
import re
import uuid
from datetime import datetime, timedelta
from flask import flash
from sqlalchemy import func
from extensions import db
from models import User, Category, Product, Order


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    return text.strip("-")


def generate_order_number():
    """Generate unique order number."""
    return f"AS{datetime.utcnow().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


# Local images in static/images/products/ — matched to product names
PRODUCT_IMAGES_BY_SLUG = {
    "sandalwood-incense-sticks-100-pcs": "images/products/sandalwood-incense.jpg",
    "brass-pooja-thali-set": "images/products/pooja-thali.jpg",
    "lord-ganesha-brass-idol-6-inch": "images/products/ganesha-idol.jpg",
    "bhagavad-gita-hindi-hardcover": "images/products/bhagavad-gita.jpg",
    "diwali-complete-pooja-kit": "images/products/diwali-kit.jpg",
    "navratri-durga-pooja-kit": "images/products/navratri-kit.jpg",
    "rudraksha-mala-108-beads": "images/products/rudraksha-mala.jpg",
    "camphor-tablets-50-pcs": "images/products/camphor.jpg",
    "online-satyanarayan-pooja-booking": "images/products/satyanarayan-pooja.jpg",
    "griha-pravesh-pooja-service": "images/products/griha-pravesh.jpg",
    "copper-kalash-with-plate": "images/products/copper-kalash.jpg",
    "holi-color-pooja-combo-kit": "images/products/holi-kit.jpg",
}


def get_product_image(slug):
    """Return static image path for a product slug."""
    return PRODUCT_IMAGES_BY_SLUG.get(slug, "images/placeholder.jpg")


def refresh_product_images():
    """Sync database image_url with local name-matched product images."""
    updated = 0
    for product in Product.query.all():
        new_path = get_product_image(product.slug)
        if product.image_url != new_path:
            product.image_url = new_path
            updated += 1
    if updated:
        db.session.commit()


def seed_database(app):
    """Seed categories, products, and admin user from env."""
    with app.app_context():
        from config import Config

        # Create admin from environment variables
        admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                name=Config.ADMIN_NAME,
                email=Config.ADMIN_EMAIL,
                is_admin=True,
            )
            admin.set_password(Config.ADMIN_PASSWORD)
            db.session.add(admin)
            db.session.commit()

        # Always fix broken/outdated image URLs in existing database
        refresh_product_images()

        if Category.query.count() > 0:
            return

        categories_data = [
            ("Incense & Dhoop", "incense-dhoop", "Premium incense sticks, dhoop, and camphor."),
            ("Pooja Thali & Items", "pooja-thali", "Complete pooja thali sets and ritual items."),
            ("Idols & Murtis", "idols-murtis", "Brass, marble, and clay idols for home temple."),
            ("Holy Books & Yantras", "holy-books", "Ramayan, Bhagavad Gita, yantras and malas."),
            ("Festival Kits", "festival-kits", "Ready-made kits for Diwali, Navratri, and more."),
            ("Spiritual Services", "spiritual-services", "Online pooja booking and priest services."),
        ]

        categories = {}
        for name, slug, desc in categories_data:
            cat = Category(name=name, slug=slug, description=desc)
            db.session.add(cat)
            categories[slug] = cat
        db.session.commit()

        # Refresh category IDs
        for slug in categories:
            categories[slug] = Category.query.filter_by(slug=slug).first()

        products_data = [
            {
                "name": "Sandalwood Incense Sticks (100 pcs)",
                "description": "Pure sandalwood fragrance incense sticks for daily pooja and meditation. Long burning, smoke-free formula.",
                "price": 249.0,
                "stock": 150,
                "image_url": "images/products/sandalwood-incense.jpg",
                "category": "incense-dhoop",
                "featured": True,
                "festival": False,
            },
            {
                "name": "Brass Pooja Thali Set",
                "description": "Elegant brass thali with diya, kalash, bell, and incense holder. Perfect for daily worship.",
                "price": 1299.0,
                "stock": 80,
                "image_url": "images/products/pooja-thali.jpg",
                "category": "pooja-thali",
                "featured": True,
                "festival": False,
            },
            {
                "name": "Lord Ganesha Brass Idol (6 inch)",
                "description": "Handcrafted brass Ganesha murti with antique finish. Ideal for home temple and gifting.",
                "price": 1899.0,
                "stock": 45,
                "image_url": "images/products/ganesha-idol.jpg",
                "category": "idols-murtis",
                "featured": True,
                "festival": False,
            },
            {
                "name": "Bhagavad Gita (Hindi) Hardcover",
                "description": "Authentic Hindi translation with commentary. Premium hardcover edition for daily reading.",
                "price": 399.0,
                "stock": 200,
                "image_url": "images/products/bhagavad-gita.jpg",
                "category": "holy-books",
                "featured": False,
                "festival": False,
            },
            {
                "name": "Diwali Complete Pooja Kit",
                "description": "All-in-one Diwali kit: diyas, rangoli colors, incense, sweets box, Lakshmi-Ganesh idols, and camphor.",
                "price": 2499.0,
                "stock": 60,
                "image_url": "images/products/diwali-kit.jpg",
                "category": "festival-kits",
                "featured": True,
                "festival": True,
            },
            {
                "name": "Navratri Durga Pooja Kit",
                "description": "Nine-day Navratri essentials: red chunri, kalash, coconut, flowers guide, incense, and prasad box.",
                "price": 1999.0,
                "stock": 55,
                "image_url": "images/products/navratri-kit.jpg",
                "category": "festival-kits",
                "featured": True,
                "festival": True,
            },
            {
                "name": "Rudraksha Mala (108 beads)",
                "description": "Authentic 5-mukhi rudraksha mala for japa and meditation. Lab-tested beads with certificate.",
                "price": 899.0,
                "stock": 90,
                "image_url": "images/products/rudraksha-mala.jpg",
                "category": "holy-books",
                "featured": False,
                "festival": False,
            },
            {
                "name": "Camphor Tablets (50 pcs)",
                "description": "Pure bhimseni camphor for aarti. Smokeless and long-lasting tablets.",
                "price": 149.0,
                "stock": 300,
                "image_url": "images/products/camphor.jpg",
                "category": "incense-dhoop",
                "featured": False,
                "festival": False,
            },
            {
                "name": "Online Satyanarayan Pooja Booking",
                "description": "Book experienced priest for Satyanarayan Katha at home or online. Includes samagri list guidance.",
                "price": 3100.0,
                "stock": 999,
                "image_url": "images/products/satyanarayan-pooja.jpg",
                "category": "spiritual-services",
                "featured": True,
                "festival": False,
            },
            {
                "name": "Griha Pravesh Pooja Service",
                "description": "Complete housewarming ritual with Vedic priest. Duration 2-3 hours. Pan-India availability.",
                "price": 5100.0,
                "stock": 999,
                "image_url": "images/products/griha-pravesh.jpg",
                "category": "spiritual-services",
                "featured": False,
                "festival": False,
            },
            {
                "name": "Copper Kalash with Plate",
                "description": "Traditional copper kalash for pooja. Includes plate and coconut holder.",
                "price": 749.0,
                "stock": 70,
                "image_url": "images/products/copper-kalash.jpg",
                "category": "pooja-thali",
                "featured": False,
                "festival": False,
            },
            {
                "name": "Holi Color & Pooja Combo Kit",
                "description": "Organic gulal colors with Holika dahan samagri and prayer guide booklet.",
                "price": 899.0,
                "stock": 40,
                "image_url": "images/products/holi-kit.jpg",
                "category": "festival-kits",
                "featured": False,
                "festival": True,
            },
        ]

        for pdata in products_data:
            cat = categories[pdata["category"]]
            product_slug = slugify(pdata["name"])
            product = Product(
                name=pdata["name"],
                slug=product_slug,
                description=pdata["description"],
                price=pdata["price"],
                stock=pdata["stock"],
                image_url=get_product_image(product_slug),
                category_id=cat.id,
                is_featured=pdata["featured"],
                is_festival_kit=pdata["festival"],
            )
            db.session.add(product)

        db.session.commit()


def get_sales_analytics():
    """Return data for Chart.js analytics."""
    # Last 6 months sales
    months = []
    sales = []
    now = datetime.utcnow()

    for i in range(5, -1, -1):
        month_start = (now.replace(day=1) - timedelta(days=i * 30)).replace(day=1)
        if i > 0:
            month_end = (month_start + timedelta(days=32)).replace(day=1)
        else:
            month_end = now

        total = (
            db.session.query(func.coalesce(func.sum(Order.total_amount), 0))
            .filter(
                Order.created_at >= month_start,
                Order.created_at < month_end,
                Order.status != "Cancelled",
            )
            .scalar()
        )
        months.append(month_start.strftime("%b %Y"))
        sales.append(float(total or 0))

    # Order status counts
    status_labels = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    status_counts = []
    for status in status_labels:
        count = Order.query.filter_by(status=status).count()
        status_counts.append(count)

    # Top categories by revenue
    from models import OrderItem

    category_sales = (
        db.session.query(Category.name, func.sum(OrderItem.subtotal))
        .join(Product, Product.id == OrderItem.product_id)
        .join(Category, Category.id == Product.category_id)
        .group_by(Category.name)
        .order_by(func.sum(OrderItem.subtotal).desc())
        .limit(5)
        .all()
    )

    cat_labels = [c[0] for c in category_sales] or ["No Data"]
    cat_values = [float(c[1] or 0) for c in category_sales] or [0]

    return {
        "months": months,
        "sales": sales,
        "status_labels": status_labels,
        "status_counts": status_counts,
        "cat_labels": cat_labels,
        "cat_values": cat_values,
    }
