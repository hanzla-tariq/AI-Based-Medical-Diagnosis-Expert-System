import os
from flask import Flask
from .config import config
from .extensions import db, login_manager, bcrypt, cors


def create_app(config_name='default'):
    """Flask application factory."""
    # Set static and template folders to frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')

    app = Flask(
        __name__,
        static_folder=os.path.join(frontend_dir, 'static'),
        template_folder=os.path.join(frontend_dir, 'templates')
    )

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Register Blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.diagnosis import diagnosis_bp
    from .routes.reports import reports_bp
    from .routes.history import history_bp
    from .routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(diagnosis_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_bp)

    # Register landing page route
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    # User loader for Flask-Login
    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create database tables
    with app.app_context():
        from .models import user, consultation
        db.create_all()

        # Seed default admin account
        from .seed_admin import seed_admin
        seed_admin(app)

    return app
