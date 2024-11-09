from app import db


class ProfessionalDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(
        db.Integer, db.ForeignKey("service.id", ondelete="SET NULL"), nullable=True
    )
    description = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    document = db.Column(db.String(50), nullable=False)
    extra_price = db.Column(db.Integer, default=0)
    is_approved = db.Column(db.Boolean, default=False)
    username = db.Column(db.String(20), db.ForeignKey("user.username"), nullable=False)
    ## TODO: Add Service relationship,
    ## TODO: Add Business name
    user = db.relationship("User", back_populates="professional_details")
    service_requests = db.relationship(
        "ServiceRequest", back_populates="professional_details", lazy=True
    )

    def block(self):
        self.is_approved = False
        db.session.commit()
