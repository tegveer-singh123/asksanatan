"""Shopping cart and checkout blueprint."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import Product, CartItem, Order, OrderItem
from forms import CheckoutForm
from utils import generate_order_number

cart_bp = Blueprint("cart", __name__)


def get_cart_items():
    """Get current user's cart items."""
    return CartItem.query.filter_by(user_id=current_user.id).all()


def cart_total(items):
    """Calculate cart total."""
    return sum(item.product.price * item.quantity for item in items)


@cart_bp.route("/cart")
@login_required
def view_cart():
    """View shopping cart."""
    items = get_cart_items()
    total = cart_total(items)
    return render_template("shop/cart.html", items=items, total=total)


@cart_bp.route("/cart/add/<int:product_id>", methods=["POST"])
@login_required
def add_to_cart(product_id):
    """Add product to cart."""
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get("quantity", 1, type=int)

    if quantity < 1:
        flash("Invalid quantity.", "danger")
        return redirect(request.referrer or url_for("shop.products"))

    if product.stock < quantity:
        flash("Insufficient stock available.", "warning")
        return redirect(request.referrer or url_for("shop.product_detail", slug=product.slug))

    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, product_id=product.id
    ).first()

    if cart_item:
        new_qty = cart_item.quantity + quantity
        if new_qty > product.stock:
            flash("Cannot add more than available stock.", "warning")
            return redirect(request.referrer or url_for("shop.view_cart"))
        cart_item.quantity = new_qty
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    flash(f"{product.name} added to cart!", "success")
    return redirect(request.referrer or url_for("cart.view_cart"))


@cart_bp.route("/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):
    """Update cart item quantity."""
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = request.form.get("quantity", 1, type=int)

    if quantity < 1:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from cart.", "info")
        return redirect(url_for("cart.view_cart"))

    if quantity > item.product.stock:
        flash("Quantity exceeds available stock.", "warning")
        return redirect(url_for("cart.view_cart"))

    item.quantity = quantity
    db.session.commit()
    flash("Cart updated.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/cart/remove/<int:item_id>", methods=["POST"])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart."""
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Item removed from cart.", "info")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    """Checkout and place order."""
    items = get_cart_items()
    if not items:
        flash("Your cart is empty. Add products before checkout.", "warning")
        return redirect(url_for("shop.products"))

    total = cart_total(items)
    form = CheckoutForm()

    # Pre-fill from profile
    if request.method == "GET":
        form.shipping_name.data = current_user.name
        form.shipping_phone.data = current_user.phone
        form.shipping_address.data = current_user.address
        form.shipping_city.data = current_user.city
        form.shipping_pincode.data = current_user.pincode

    if form.validate_on_submit():
        order = Order(
            user_id=current_user.id,
            order_number=generate_order_number(),
            total_amount=total,
            payment_method=form.payment_method.data,
            shipping_name=form.shipping_name.data.strip(),
            shipping_phone=form.shipping_phone.data.strip(),
            shipping_address=form.shipping_address.data.strip(),
            shipping_city=form.shipping_city.data.strip(),
            shipping_pincode=form.shipping_pincode.data.strip(),
            notes=form.notes.data.strip() if form.notes.data else None,
        )
        db.session.add(order)
        db.session.flush()

        for item in items:
            if item.quantity > item.product.stock:
                db.session.rollback()
                flash(f"Insufficient stock for {item.product.name}.", "danger")
                return redirect(url_for("cart.view_cart"))

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product.id,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price,
                subtotal=item.product.price * item.quantity,
            )
            db.session.add(order_item)
            item.product.stock -= item.quantity

        # Clear cart
        for item in items:
            db.session.delete(item)

        db.session.commit()
        flash("Order placed successfully!", "success")
        return redirect(url_for("shop.order_success", order_number=order.order_number))

    return render_template("shop/checkout.html", form=form, items=items, total=total)
