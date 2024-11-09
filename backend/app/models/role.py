from app import db
from sqlalchemy.orm import validates

ALLOWED_ROLES = ["admin", "customer", "professional"]


class Role(db.Model):
    # admin, customer, professional
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)

    @validates("name")
    def validate_name(self, key, name):
        if not name:
            raise AssertionError("Role name is required.")
        if name != name.lower():
            raise AssertionError("Role name must be in lowercase.")
        if name not in ALLOWED_ROLES:
            raise AssertionError(f"Role name must be one of {ALLOWED_ROLES}")
        return name

    @classmethod
    def create_default_roles(cls):
        """Create default roles and an admin user if they do not exist."""

        for role_name in ALLOWED_ROLES:
            role = cls.query.filter_by(name=role_name).first()
            if not role:
                role = cls(name=role_name)
                db.session.add(role)

        db.session.commit()
