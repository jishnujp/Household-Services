from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Blueprint,
)
from datetime import datetime
from sqlalchemy import or_
import plotly.express as px
import plotly.io as pio
from app.models import User, ProfessionalDetails, Service, ServiceRequest
from app.utils import login_required
from app import db


customer_view_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_view_bp.route("/home", methods=["GET"])
@login_required("customer")
def home():
    service_id = request.args.get("service")
    request_history = ServiceRequest.query.filter_by(customer_id=session["user"]).all()
    if service_id and service_id != "all":

        # get ProfessionalDetails for the selected service that are approved
        professionals = (
            ProfessionalDetails.query.filter_by(service_id=service_id)
            .filter_by(is_approved=True)
            .all()
        )
        # get the selected service
        selected_service = Service.query.get(service_id)
        return render_template(
            "customer/home.html",
            professionals=professionals,
            selected_service=selected_service,
            request_history=request_history,
        )
    all_service = Service.query.filter(Service.name != "NoService").all()
    return render_template(
        "customer/home.html", services=all_service, request_history=request_history
    )


@customer_view_bp.route("/search", methods=["GET", "POST"])
@login_required("customer")
def search():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        search_by = request.form.get("search_by")
        professionals = []
        if search_by == "service":
            services = Service.query.filter(
                Service.name.ilike(f"%{search_query}%")
            ).all()
            professionals = [
                professional
                for service in services
                for professional in service.professionals
                if professional.is_approved
            ]
        elif search_by == "professional":
            professionals = (
                ProfessionalDetails.query.join(User)
                .filter(
                    or_(
                        User.username.ilike(f"%{search_query}%"),
                        ProfessionalDetails.business_name.ilike(f"%{search_query}%"),
                        User.full_name.ilike(f"%{search_query}%"),
                    )
                )
                .all()
            )
        elif search_by == "pincode":
            professionals = (
                ProfessionalDetails.query.join(User)
                .filter(User.pincode.ilike(f"%{search_query}%"))
                .all()
            )
        else:
            flash("Invalid search criteria", "danger")
            return redirect(url_for("customer.home"))
        return render_template("customer/search.html", professionals=professionals)
    else:
        return render_template("customer/search.html")


@customer_view_bp.route("/summary")
@login_required("customer")
def summary():
    all_service_requests = ServiceRequest.query.filter_by(
        customer_id=session["user"]
    ).all()

    status_count = {}
    for service_request in all_service_requests:
        if service_request.status not in status_count:
            status_count[service_request.status] = 1
        else:
            status_count[service_request.status] += 1
    status_fig = px.pie(
        values=list(status_count.values()),
        names=list(status_count.keys()),
        title="Service Request Status",
    )

    status_plot_html = pio.to_html(status_fig, full_html=False)
    return render_template(
        "customer/summary.html",
        status_plot_html=status_plot_html,
    )


@customer_view_bp.route("/book/<int:id>", methods=["GET", "POST"])
@login_required("customer")
def book_service(id):
    professional = ProfessionalDetails.query.get(id)

    user = User.query.get(session["user"])
    # TODO: Check if the professinoal is approved
    if request.method == "POST":
        print(f"Service requested by {user.username} to {professional.user.username}")
        service_date = request.form.get("service_date")
        service_date = datetime.strptime(service_date, "%Y-%m-%d")
        service_request = ServiceRequest(
            customer_id=session["user"],
            professional_details_id=id,
            service_id=professional.service_id,
            date_of_service=service_date,
            remarks=request.form.get("remarks"),
            professional_details=professional,
            user=user,
        )
        db.session.add(service_request)
        db.session.commit()
        flash("Service booked successfully", "success")
        return redirect(url_for("customer.home"))
    elif request.method == "GET":
        return render_template("customer/book.html", professional=professional)


# submit_review
@customer_view_bp.route("/submit_review/<int:id>", methods=["POST"])
@login_required("customer")
def submit_review(id):
    service_request = ServiceRequest.query.get(id)
    service_request.review = request.form.get("review")
    service_request.rating = int(request.form.get("rating"))
    db.session.commit()
    print(f"Review submitted for service request {id}")
    print(f"Review: {service_request.review}")
    print(f"Rating: {service_request.rating}")
    flash("Review submitted successfully", "success")
    return redirect(url_for("customer.home"))
