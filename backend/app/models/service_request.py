from sqlalchemy import Enum, CheckConstraint
from app import db
from app.models.base_model import BaseModel
from app.utils.constants import ServiceRequestStatus


class ServiceRequest(BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    professional_details_id = db.Column(
        db.Integer, db.ForeignKey("professional_details.id"), nullable=False
    )
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"), nullable=False)
    date_of_service = db.Column(db.Date, nullable=False)
    status = db.Column(
        Enum(*ServiceRequestStatus.all(), name="service_request_status_enum"),
        nullable=False,
        default=ServiceRequestStatus.PENDING,
    )
    remarks = db.Column(db.String(100), nullable=False)
    review = db.Column(db.String(100), nullable=True)
    rating = db.Column(db.Integer, nullable=True)

    cust_issue_raised = db.Column(db.Boolean, default=False)
    prof_issue_raised = db.Column(db.Boolean, default=False)

    professional_details = db.relationship(
        "ProfessionalDetails", back_populates="service_requests", lazy="select"
    )
    user = db.relationship("User", back_populates="requested_services")

    __table_args__ = (
        CheckConstraint("rating BETWEEN 1 AND 5", name="check_service_request_rating"),
    )

    ## TODO: Customer and professional should not be able to rasie issue for service requests

    # @validates("date_of_service")
    # def validate_date_of_service(self, key, date_of_service):
    #     assert (
    #         date_of_service > datetime.utcnow()
    #     ), "Date of service should be in future"
    #     return date_of_service
