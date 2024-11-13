from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    session,
    Blueprint,
)
from datetime import datetime
from app.models import User, ServiceRequest
from app.utils import login_required
from app import db

professional_view_bp = Blueprint("professional", __name__, url_prefix="/professional")


@professional_view_bp.route("/home")
@login_required("professional")
def home():
    print(session["user"])
    professional = User.query.get(session["user"]).professional_details
    service_requests = ServiceRequest.query.filter_by(
        professional_details_id=professional.id
    ).all()
    todays_services, upcoming_services = [], []
    # todays date
    today = datetime.now()
    for service in service_requests:
        # compare only date, not time
        if service.date_of_service == today.date():
            todays_services.append(service)
        elif service.date_of_service > today.date():
            upcoming_services.append(service)
    completed_services = [
        service for service in service_requests if service.status == "Completed"
    ]
    return render_template(
        "professional/home.html",
        professional=professional,
        todays_services=todays_services,
        upcoming_services=upcoming_services,
        completed_services=completed_services,
    )


@professional_view_bp.route("/search")
@login_required("professional")
def search():
    return render_template("professional/search.html")


@professional_view_bp.route("/summary")
@login_required("professional")
def summary():
    return render_template("professional/summary.html")


@professional_view_bp.route("/accept_service/<int:id>")
@login_required("professional")
def accept_service_request(id):
    service_request = ServiceRequest.query.get(id)
    service_request.status = "Accepted"
    db.session.commit()
    flash("Service accepted", "success")
    return redirect(url_for("professional.home"))


@professional_view_bp.route("/reject_service/<int:id>")
@login_required("professional")
def reject_service_request(id):
    service_request = ServiceRequest.query.get(id)
    service_request.status = "Rejected"
    db.session.commit()
    flash("Service rejected", "success")
    return redirect(url_for("professional.home"))


# close the service request
@professional_view_bp.route("/close_service/<int:id>")
@login_required("professional")
def close_service_request(id):
    service_request = ServiceRequest.query.get(id)
    service_request.status = "Completed"
    db.session.commit()
    flash("Service completed", "success")
    return redirect(url_for("professional.home"))
