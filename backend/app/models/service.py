from app import db
from datetime import datetime, timezone


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Integer, nullable=False)

    professionals = db.relationship("ProfessionalDetails", backref="service", lazy=True)

    # soft delete
    is_active = db.Column(db.Boolean, default=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = datetime.now(timezone.utc)
        # block all professionals associated with this service
        for professional in self.professionals:
            professional.block()
        db.session.commit()
