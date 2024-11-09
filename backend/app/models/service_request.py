from app import db
from datetime import datetime, timezone
from sqlalchemy.orm import validates


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    professional_details_id = db.Column(
        db.Integer, db.ForeignKey("professional_details.id"), nullable=False
    )
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    date_of_request = db.Column(
        db.DateTime, nullable=False, default=datetime.now(timezone.utc)
    )
    date_of_service = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Pending")
    remarks = db.Column(db.String(100), nullable=False)
    review = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    professional_details = db.relationship(
        "ProfessionalDetails", back_populates="service_requests", lazy=True
    )
    user = db.relationship("User", back_populates="requested_services")

    # @validates("date_of_service")
    # def validate_date_of_service(self, key, date_of_service):
    #     assert (
    #         date_of_service > datetime.utcnow()
    #     ), "Date of service should be in future"
    #     return date_of_service

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
