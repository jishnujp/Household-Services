from app import db
from sqlalchemy import Enum
from app.utils.constants import AllowableRoles


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        Enum(*AllowableRoles.all(), name="allowable_roles_enum"),
        nullable=False,
        unique=True,
    )
    users = db.relationship(
        "User", secondary="user_role", back_populates="roles", lazy="select"
    )

    @classmethod
    def create_default_roles(cls):
        """Create default roles if they do not exist."""
        existing_roles = {role.name for role in cls.query.all()}
        missing_roles = set(AllowableRoles.all()) - existing_roles

        if missing_roles:
            db.session.add_all([cls(name=role_name) for role_name in missing_roles])
            db.session.commit()

    def __repr__(self):
        return f"<Role {self.id}: {self.name}>"
