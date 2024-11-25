from app import db
from app.models.base_model import BaseModel


class ProfessionalDetails(BaseModel):
    id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        primary_key=True,
        nullable=False,
        autoincrement=False,
    )
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", ondelete="SET NULL"), nullable=True
    )
    business_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    document = db.Column(db.String(50), nullable=False)
    extra_price = db.Column(db.Integer, default=0)
    avg_rating = db.Column(db.Float, default=0)
    service = db.relationship("Service", back_populates="professionals")
    user = db.relationship("User", back_populates="professional_details")
    service_requests = db.relationship(
        "ServiceRequest", back_populates="professional_details", lazy="select"
    )
