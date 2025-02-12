from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from flask_restful import Api
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class=Config):
    # Create and configure the Flask application
    print("Creating app####")
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app context
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    api = Api(app)

    login_manager.login_view = "public.login"
    login_manager.login_message = "Please log in to access this page"

    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Role, Service, ProfessionalDetails

        return {
            "db": db,
            "User": User,
            "Role": Role,
            "Service": Service,
            "ProfessionalDetails": ProfessionalDetails,
        }

    from app.views import (
        public_view_bp,
        admin_view_bp,
        customer_view_bp,
        professional_view_bp,
    )

    app.register_blueprint(public_view_bp)
    app.register_blueprint(admin_view_bp)
    app.register_blueprint(customer_view_bp)
    app.register_blueprint(professional_view_bp)

    from app.routes import public_api_bp

    app.register_blueprint(public_api_bp, url_prefix="/api")

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return "Internal server error", 500

    return app
