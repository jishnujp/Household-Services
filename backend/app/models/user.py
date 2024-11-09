from app import db
from sqlalchemy.orm import validates


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    profile_pic = db.Column(db.String(20), default="default.jpg")
    pincode = db.Column(db.String(6))
    phone = db.Column(db.String(15))

    roles = db.relationship(
        "Role", secondary="user_role", backref=db.backref("users", lazy=True)
    )
    professional_details = db.relationship(
        "ProfessionalDetails", back_populates="user", lazy=True, uselist=False
    )
    requested_services = db.relationship(
        "ServiceRequest", back_populates="user", lazy=True
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

        if not User.query.filter_by(username="admin@admin").first():
            admin_user = User(
                username="admin@admin",
                password="admin",
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
        return password
