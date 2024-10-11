from flask import Flask
from application.database import db
from application.config import Config
from application.models import *    

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

        # create the roles
        admin_role = Role.query.filter_by(name = 'admin').first()
        if not admin_role:
            admin_role = Role(name = 'admin')
            db.session.add(admin_role)

        if not Role.query.filter_by(name = 'customer').first():
            db.session.add(Role(name='customer'))

        professional_role = Role.query.filter_by(name = 'professional').first()
        if not Role.query.filter_by(name = 'professional').first():
            professional_role = Role(name = 'professional')
            db.session.add(professional_role)

        # create admin user if not exist
        if not User.query.filter_by(username = 'admin').first():
            admin_user = User(
                username = 'admin',
                password = 'admin',
                roles = [admin_role, professional_role]
            )
            db.session.add(admin_user)

        db.session.commit()


    return app
