from flask import render_template, redirect, url_for, flash, session, Blueprint, request
from datetime import datetime
from sqlalchemy import or_
import plotly.express as px
import plotly.io as pio
from app.models import User, ServiceRequest, ProfessionalDetails
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


@professional_view_bp.route("/search", methods=["GET", "POST"])
@login_required("professional")
def search():
    if request.method == "POST":
        search_query = request.form["search_query"]
        search_by = request.form["search_by"]
        if search_by == "date":
            service_requests = ServiceRequest.query.filter_by(
                date_of_service=search_query
            ).all()
        elif search_by == "user":
            service_requests = (
                ServiceRequest.query.join(User)
                .filter(
                    or_(
                        User.address.like(f"%{search_query}%"),
                        User.full_name.like(f"%{search_query}%"),
                        User.username.like(f"%{search_query}%"),
                        User.phone.like(f"%{search_query}%"),
                        User.pincode.like(f"%{search_query}%"),
                    )
                )
                .all()
            )

        else:
            flash("Invalid search criteria", "danger")
            return redirect(url_for("professional.search"))

        return render_template(
            "professional/search.html", service_requests=service_requests
        )

    return render_template("professional/search.html")


@professional_view_bp.route("/summary")
@login_required("professional")
def summary():
    customer_ratings = {i: 0 for i in range(6)}
    all_service_requests = ServiceRequest.query.filter_by(
        professional_details_id=session["user"]
    )
    for service_request in all_service_requests:
        if service_request.rating:
            customer_ratings[service_request.rating] += 1
        else:
            customer_ratings[0] += 1
    rating_fig = px.bar(
        x=list(customer_ratings.keys()),
        y=list(customer_ratings.values()),
        title="Customer Ratings",
        labels={"x": "Rating", "y": "Count"},
    )
    rating_fig = pio.to_html(rating_fig)
    return render_template("professional/summary.html", rating_fig=rating_fig)


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
