from sqlalchemy.orm import validates
import os
from flask_login import UserMixin
from app import db
from app.models.base_model import BaseModel


class User(BaseModel, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    profile_pic = db.Column(db.String(20), default="default_profile.jpg")
    pincode = db.Column(db.String(6))
    phone = db.Column(db.String(15))

    roles = db.relationship(
        "Role", secondary="user_role", back_populates="users", lazy="select"
    )
    professional_details = db.relationship(
        "ProfessionalDetails", back_populates="user", uselist=False, lazy="select"
    )
    requested_services = db.relationship(
        "ServiceRequest", back_populates="user", lazy="select"
    )

    @classmethod
    def create_admin_user(cls):
        """Create admin user if not exist."""
        from app.models.role import Role

        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            Role.create_default_roles()
            admin_role = Role.query.filter_by(name="admin").first()

        professional_role = Role.query.filter_by(name="professional").first()

        if not User.get_user(os.getenv("ADMIN_USERNAME", "admin@admin")):
            admin_user = User(
                username=os.getenv("ADMIN_USERNAME", "admin@admin"),
                password=os.getenv("ADMIN_PASSWORD", "Admin123"),
                roles=[admin_role, professional_role],
            )
            db.session.add(admin_user)
            db.session.commit()

    @validates("username")
    def validate_username(self, key, username):
        if not username:
            raise AssertionError("Username is required.")
        if len(username) < 5 or len(username) > 20:
            raise AssertionError("Username must be between 5 and 20 characters.")
        return username

    @validates("password")
    def validate_password(self, key, password):
        if not password:
            raise AssertionError("Password is required.")
        if len(password) < 5 or len(password) > 20:
            raise AssertionError("Password must be between 5 and 20 characters.")
        # check strength of password
        if not any(char.isdigit() for char in password):
            raise AssertionError("Password must have at least one digit.")
        if not any(char.isupper() for char in password):
            raise AssertionError("Password must have at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise AssertionError("Password must have at least one lowercase letter.")
        return password

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"

    @classmethod
    def get_user(cls, k):
        if type(k) == int:
            return cls.query.get(k)
        elif type(k) == str:
            return cls.query.filter_by(username=k).first()
        print(f"Invalid type to get user with {k} of type {type(k)}")
        return None

    def get_id(self):
        return str(self.id)

    def is_active(self):
        return not self.is_deactivated
