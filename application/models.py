from sqlalchemy.orm import validates
from application.database import db
from datetime import datetime


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


class Role(db.Model):
    # admin, customer, professional
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)


class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)


class ProfessionalDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
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


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Integer, nullable=False)

    professionals = db.relationship("ProfessionalDetails", backref="service", lazy=True)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    professional_details_id = db.Column(
        db.Integer, db.ForeignKey("professional_details.id"), nullable=False
    )
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_of_service = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    remarks = db.Column(db.String(100), nullable=False)
    review = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    professional_details = db.relationship(
        "ProfessionalDetails", back_populates="service_requests", lazy=True
    )
    user = db.relationship("User", back_populates="requested_services")

    @validates("date_of_service")
    def validate_date_of_service(self, key, date_of_service):
        assert (
            date_of_service > datetime.utcnow()
        ), "Date of service should be in future"
        return date_of_service

    @validates("status")
    def validate_status(self, key, status):
        assert status in [
            "Pending",
            "Accepted",
            "Rejected",
            "Completed",
        ], "Invalid Status"
        return status

    @validates("rating")
    def validate_rating(self, key, rating):
        assert rating in range(1, 6), "Rating should be between 1 and 5"
        return rating
