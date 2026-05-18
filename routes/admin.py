"""Admin dashboard blueprint."""
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Product, Category, Order, OrderItem
from forms import ProductForm, CategoryForm
from utils import slugify, get_sales_analytics

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    """Decorator to restrict access to admin users."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin access required.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    """Admin dashboard with analytics."""
    total_users = User.query.filter_by(is_admin=False).count()
    total_products = Product.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.status != "Cancelled"
    ).scalar() or 0

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    analytics = get_sales_analytics()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        recent_orders=recent_orders,
        analytics=analytics,
    )


@admin_bp.route("/products")
@login_required
@admin_required
def products():
    """List all products for admin."""
    products_list = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=products_list)


@admin_bp.route("/products/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    """Add new product."""
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        slug = slugify(form.name.data)
        if Product.query.filter_by(slug=slug).first():
            slug = f"{slug}-{Product.query.count() + 1}"

        product = Product(
            name=form.name.data.strip(),
            slug=slug,
            description=form.description.data.strip(),
            price=form.price.data,
            stock=form.stock.data,
            image_url=form.image_url.data.strip(),
            category_id=form.category_id.data,
            is_featured=form.is_featured.data,
            is_festival_kit=form.is_festival_kit.data,
        )
        db.session.add(product)
        db.session.commit()
        flash("Product added successfully!", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", form=form, title="Add Product")


@admin_bp.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    """Edit existing product."""
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.all()]

    if form.validate_on_submit():
        product.name = form.name.data.strip()
        product.description = form.description.data.strip()
        product.price = form.price.data
        product.stock = form.stock.data
        product.image_url = form.image_url.data.strip()
        product.category_id = form.category_id.data
        product.is_featured = form.is_featured.data
        product.is_festival_kit = form.is_festival_kit.data
        db.session.commit()
        flash("Product updated successfully!", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/product_form.html", form=form, title="Edit Product", product=product)


@admin_bp.route("/products/delete/<int:product_id>", methods=["POST"])
@login_required
@admin_required
def delete_product(product_id):
    """Delete product."""
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted.", "info")
    return redirect(url_for("admin.products"))


@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    """Manage categories."""
    form = CategoryForm()
    categories_list = Category.query.all()

    if form.validate_on_submit():
        slug = slugify(form.name.data)
        if Category.query.filter_by(slug=slug).first():
            flash("Category already exists.", "warning")
        else:
            category = Category(
                name=form.name.data.strip(),
                slug=slug,
                description=form.description.data.strip() if form.description.data else None,
            )
            db.session.add(category)
            db.session.commit()
            flash("Category added!", "success")
            return redirect(url_for("admin.categories"))

    return render_template("admin/categories.html", form=form, categories=categories_list)


@admin_bp.route("/categories/delete/<int:category_id>", methods=["POST"])
@login_required
@admin_required
def delete_category(category_id):
    """Delete category if no products."""
    category = Category.query.get_or_404(category_id)
    if category.products:
        flash("Cannot delete category with existing products.", "danger")
    else:
        db.session.delete(category)
        db.session.commit()
        flash("Category deleted.", "info")
    return redirect(url_for("admin.categories"))


@admin_bp.route("/users")
@login_required
@admin_required
def users():
    """View all users."""
    users_list = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users_list)


@admin_bp.route("/orders")
@login_required
@admin_required
def orders():
    """View and manage all orders."""
    status_filter = request.args.get("status", "")
    query = Order.query.order_by(Order.created_at.desc())
    if status_filter:
        query = query.filter_by(status=status_filter)
    orders_list = query.all()
    return render_template("admin/orders.html", orders=orders_list, status_filter=status_filter)


@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
@admin_required
def update_order_status(order_id):
    """Update order status."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status", "Pending")
    valid_statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
    if new_status in valid_statuses:
        order.status = new_status
        db.session.commit()
        flash(f"Order {order.order_number} status updated to {new_status}.", "success")
    else:
        flash("Invalid status.", "danger")
    return redirect(url_for("admin.orders"))


@admin_bp.route("/orders/<order_number>")
@login_required
@admin_required
def order_detail(order_number):
    """Admin view order detail."""
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    return render_template("shop/order_detail.html", order=order, admin_view=True)
