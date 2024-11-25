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
import plotly.express as px
import plotly.io as pio
from app.models import Service
from app.utils import login_required
from app import db
from app.controllers import (
    search_professional,
    search_service,
    create_service_request,
    search_service_requests,
)


customer_view_bp = Blueprint("customer", __name__, url_prefix="/customer")


@customer_view_bp.route("/home", methods=["GET"])
@login_required("customer")
def home():
    service_id = request.args.get("service")
    request_history = search_service_requests(customer_id=session["user"])
    if service_id and service_id != "all":

        # get ProfessionalDetails for the selected service that are approved
        professionals = search_professional(service_id=service_id)
        professionals = [prof for prof in professionals if prof.is_approved]

        # get the selected service
        selected_service = search_service(id=service_id)
        return render_template(
            "customer/home.html",
            professionals=professionals,
            selected_service=selected_service,
            request_history=request_history,
        )
    all_service = Service.query.all()
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
            services = search_service(name__like=search_query)
            professionals = [
                professional
                for service in services
                for professional in service.professionals
                if professional.is_approved
            ]
        elif search_by == "professional":
            professionals = search_professional(
                username__like=search_query,
                business_name__like=search_query,
                full_name__like=search_query,
            )

        elif search_by == "pincode":
            professionals = search_professional(pincode__like=search_query)

        else:
            flash("Invalid search criteria", "danger")
            return redirect(url_for("customer.home"))
        return render_template("customer/search.html", professionals=professionals)
    else:
        return render_template("customer/search.html")


@customer_view_bp.route("/summary")
@login_required("customer")
def summary():
    all_service_requests = search_service_requests(customer_id=session["user"])

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

    if request.method == "POST":
        service_date = request.form.get("service_date")
        service_date = datetime.strptime(service_date, "%Y-%m-%d")
        stat, msg = create_service_request(
            customer_id=session["user"],
            professional_details_id=id,
            date_of_service=service_date,
            remarks=request.form.get("remarks"),
        )
        if not stat:
            flash(msg, "danger")
            return redirect(url_for("customer.home"))
        flash(msg, "success")
        return redirect(url_for("customer.home"))
    elif request.method == "GET":
        professional = search_professional(id=id)
        return render_template("customer/book.html", professional=professional)


# submit_review
@customer_view_bp.route("/submit_review/<int:id>", methods=["POST"])
@login_required("customer")
def submit_review(id):
    service_request = search_service_requests(id=id)
    service_request.review = request.form.get("review")
    service_request.rating = int(request.form.get("rating"))
    db.session.commit()
    print(f"Review submitted for service request {id}")
    print(f"Review: {service_request.review}")
    print(f"Rating: {service_request.rating}")
    flash("Review submitted successfully", "success")
    return redirect(url_for("customer.home"))
