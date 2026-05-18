"""Shop and customer dashboard blueprint."""
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import or_
from extensions import db
from models import Product, Category, Order, CartItem
from forms import CheckoutForm
from utils import generate_order_number

shop_bp = Blueprint("shop", __name__)


@shop_bp.route("/products")
def products():
    """Product listing with search and category filter."""
    query = Product.query
    search = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip()
    sort = request.args.get("sort", "newest")

    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
            )
        )

    if category_slug:
        category = Category.query.filter_by(slug=category_slug).first()
        if category:
            query = query.filter_by(category_id=category.id)

    if sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    elif sort == "name":
        query = query.order_by(Product.name.asc())
    else:
        query = query.order_by(Product.created_at.desc())

    products_list = query.all()
    categories = Category.query.all()
    return render_template(
        "shop/products.html",
        products=products_list,
        categories=categories,
        search=search,
        category_slug=category_slug,
        sort=sort,
    )


@shop_bp.route("/product/<slug>")
def product_detail(slug):
    """Single product details page."""
    product = Product.query.filter_by(slug=slug).first_or_404()
    related = (
        Product.query.filter(
            Product.category_id == product.category_id,
            Product.id != product.id,
        )
        .limit(4)
        .all()
    )
    return render_template("shop/product_detail.html", product=product, related=related)


@shop_bp.route("/dashboard")
@login_required
def dashboard():
    """User dashboard with recent orders."""
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))

    orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .limit(5)
        .all()
    )
    cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
    return render_template("shop/dashboard.html", orders=orders, cart_count=cart_count)


@shop_bp.route("/orders")
@login_required
def orders():
    """Full order history."""
    if current_user.is_admin:
        return redirect(url_for("admin.orders"))

    user_orders = (
        Order.query.filter_by(user_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("shop/orders.html", orders=user_orders)


@shop_bp.route("/order/<order_number>")
@login_required
def order_detail(order_number):
    """Invoice-style order summary."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template("shop/order_detail.html", order=order)


@shop_bp.route("/order-success/<order_number>")
@login_required
def order_success(order_number):
    """Order placement success page."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    if order.user_id != current_user.id:
        abort(403)
    return render_template("shop/order_success.html", order=order)
