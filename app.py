from flask import Flask
from application.database import db
from application.models import *
import os


def create_roles():
    """Create roles if not exist, and create admin user if not exist."""
    admin_role = Role.query.filter_by(name="admin").first()
    if not admin_role:
        admin_role = Role(name="admin")
        db.session.add(admin_role)

    if not Role.query.filter_by(name="customer").first():
        db.session.add(Role(name="customer"))

    professional_role = Role.query.filter_by(name="professional").first()
    if not Role.query.filter_by(name="professional").first():
        professional_role = Role(name="professional")
        db.session.add(professional_role)

    # Create admin user if not exist
    if not User.query.filter_by(username="admin@admin").first():
        admin_user = User(
            username="admin@admin",
            password="admin",
            roles=[admin_role, professional_role],
        )
        db.session.add(admin_user)

    db.session.commit()


def create_services():
    """Create services if not exist."""
    if not Service.query.filter_by(name="NoService").first():
        db.session.add(
            Service(name="NoService", description="No service selected", base_price=0)
        )

    db.session.commit()
    print("NoService created")


def create_static_storage(static_path):
    # create static/storage folder if not exist
    static_storage = os.path.join(static_path, "storage")
    document_storage = os.path.join(static_storage, "documents")
    profile_pic_storage = os.path.join(static_storage, "profile_pics")

    for folder in [static_storage, document_storage, profile_pic_storage]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created {folder}")


def create_app(configuration):
    app = Flask(__name__)
    app.config.from_object(configuration)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        create_roles()
        create_services()
        create_static_storage(app.static_folder)

    return app
