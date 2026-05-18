"""AskSanatan Flask Application Factory."""
from flask import Flask, render_template, url_for
from flask_wtf.csrf import CSRFProtect
from config import Config
from extensions import db, login_manager
from models import User
from utils import seed_database

csrf = CSRFProtect()


def create_app(config_class=Config):
    """Create and configure Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.template_filter("img_src")
    def img_src(path_or_url):
        """Resolve static relative paths or external URLs for img tags."""
        if not path_or_url:
            return url_for("static", filename="images/placeholder.jpg")
        if path_or_url.startswith(("http://", "https://")):
            return path_or_url
        return url_for("static", filename=path_or_url)

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.shop import shop_bp
    from routes.cart import cart_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(admin_bp)

    # Context processor for cart count
    @app.context_processor
    def inject_globals():
        from flask_login import current_user
        from models import CartItem

        cart_count = 0
        if current_user.is_authenticated and not current_user.is_admin:
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        return dict(cart_count=cart_count)

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("errors/500.html"), 500

    # Create tables and seed data
    with app.app_context():
        db.create_all()
        seed_database(app)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True, host="127.0.0.1", port=5001)
