from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    # Create and configure the Flask application
    print("Creating app####")
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with the app context
    db.init_app(app)
    migrate.init_app(app, db)

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

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return "Internal server error", 500

    return app
