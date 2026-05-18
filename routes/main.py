"""Main pages blueprint."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import Product, Category
from forms import ContactForm

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Home page with hero and featured products."""
    featured = Product.query.filter_by(is_featured=True).limit(8).all()
    festival_kits = Product.query.filter_by(is_festival_kit=True).limit(4).all()
    categories = Category.query.all()
    return render_template(
        "home.html",
        featured=featured,
        festival_kits=festival_kits,
        categories=categories,
    )


@main_bp.route("/about")
def about():
    """About page."""
    return render_template("about.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact page with form validation."""
    form = ContactForm()
    if form.validate_on_submit():
        flash("Thank you! Your message has been received. We will contact you soon.", "success")
        return redirect(url_for("main.contact"))
    return render_template("contact.html", form=form)
