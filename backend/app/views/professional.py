from flask import render_template, redirect, url_for, flash, session, Blueprint, request
from datetime import datetime
import plotly.express as px
import plotly.io as pio
from flask_login import current_user
from app.models import User
from app.utils import role_required
from app import db
from app.controllers import search_service_requests, update_professional, search_service
from app.utils.constants import AllowableRoles, ServiceRequestStatus

professional_view_bp = Blueprint(
    AllowableRoles.PROFESSIONAL, __name__, url_prefix="/professional"
)


@professional_view_bp.route("/home")
@role_required(AllowableRoles.PROFESSIONAL)
def home():
    professional = User.get_user(current_user.id).professional_details
    service_requests = search_service_requests(professional_details_id=professional.id)
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
        service
        for service in service_requests
        if service.status == ServiceRequestStatus.COMPLETED
    ]
    return render_template(
        "professional/home.html",
        professional=professional,
        todays_services=todays_services,
        upcoming_services=upcoming_services,
        completed_services=completed_services,
    )


@professional_view_bp.route("/search", methods=["GET", "POST"])
@role_required(AllowableRoles.PROFESSIONAL)
def search():
    if request.method == "POST":
        search_query = request.form["search_query"]
        search_by = request.form["search_by"]
        if search_by == "date":
            service_requests = search_service_requests(date_of_service=search_query)
        elif search_by == "user":
            service_requests = search_service_requests(
                by="customer",
                address__like=search_query,
                full_name__like=search_query,
                username__like=search_query,
                phone__like=search_query,
                pincode__like=search_query,
            )

        else:
            flash("Invalid search criteria", "danger")
            return redirect(url_for("professional.search"))

        return render_template(
            "professional/search.html", service_requests=service_requests
        )

    return render_template("professional/search.html")


@professional_view_bp.route("/summary")
@role_required(AllowableRoles.PROFESSIONAL)
def summary():
    customer_ratings = {i: 0 for i in range(6)}
    all_service_requests = search_service_requests(
        professional_details_id=current_user.id
    )
    for service_request in all_service_requests:
        if service_request.rating:
            customer_ratings[service_request.rating] += 1
        else:
            customer_ratings[0] += 1
    rating_fig = px.bar(
        x=list(customer_ratings.keys()),
        y=list(customer_ratings.values()),
        labels={"x": "Rating", "y": "Count"},
    )
    rating_fig = pio.to_html(rating_fig)
    return render_template("professional/summary.html", rating_fig=rating_fig)


@professional_view_bp.route("/accept_service/<int:id>")
@role_required(AllowableRoles.PROFESSIONAL)
def accept_service_request(id):
    service_request = search_service_requests(id=id)
    service_request.status = ServiceRequestStatus.ACCEPTED
    db.session.commit()
    flash("Service accepted", "success")
    return redirect(url_for("professional.home"))


@professional_view_bp.route("/reject_service/<int:id>")
@role_required(AllowableRoles.PROFESSIONAL)
def reject_service_request(id):
    service_request = search_service_requests(id=id)
    service_request.status = ServiceRequestStatus.REJECTED
    db.session.commit()
    flash("Service rejected", "success")
    return redirect(url_for("professional.home"))


# close the service request
@professional_view_bp.route("/close_service/<int:id>")
@role_required(AllowableRoles.PROFESSIONAL)
def close_service_request(id):
    service_request = search_service_requests(id=id)
    service_request.status = ServiceRequestStatus.COMPLETED
    db.session.commit()
    flash("Service Closed", "success")
    return redirect(url_for("professional.home"))


@professional_view_bp.route("/cancel_service/<int:id>")
@role_required(AllowableRoles.PROFESSIONAL)
def cancel_service_request(id):
    service_request = search_service_requests(id=id)
    service_request.status = "Cancelled"
    db.session.commit()
    flash("Service Cancelled", "success")
    return redirect(url_for("professional.home"))


@professional_view_bp.route("/toggle_issue/<int:id>", methods=["POST"])
@role_required(AllowableRoles.CUSTOMER)
def toggle_issue(id):
    service_request = search_service_requests(id=id)
    service_request.prof_issue_raised = not service_request.prof_issue_raised
    db.session.commit()
    flash("Issue Raised", "success")
    return redirect(url_for("professional.home"))


@professional_view_bp.route("/edit_profile", methods=["GET", "POST"])
@role_required(AllowableRoles.PROFESSIONAL)
def edit_profile():
    if request.method == "POST":
        password = request.form.get("password")
        # check if password is correct
        if not current_user.check_password(password):
            flash("Incorrect Password", "danger")
            return redirect(url_for("professional.edit_profile"))
        data = request.form.to_dict()
        for key in ["profile_pic", "document"]:
            file = request.files.get(key)
            if file:
                data[key] = file

        del data["password"]
        update_professional(
            id=current_user.id,
            data=data,
        )
        flash("Profile Updated", "success")
        return redirect(url_for("professional.home"))
    available_services = search_service()
    professional_details = User.get_user(current_user.id).professional_details
    return render_template(
        "professional/edit.html",
        available_services=available_services,
        professional_details=professional_details,
    )


@professional_view_bp.route("/change_password", methods=["POST"])
@role_required(AllowableRoles.PROFESSIONAL)
def change_password():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    cpassword = request.form.get("confirm_password")

    if not cpassword or not new_password or not old_password:
        flash("All fields are required", "danger")
        return redirect(url_for("professional.edit_profile"))
    if not cpassword == new_password:
        flash("Passwords do not match", "danger")
        return redirect(url_for("professional.edit_profile"))
    if not current_user.check_password(old_password):
        flash("Incorrect Password", "danger")
        return redirect(url_for("professional.edit_profile"))

    current_user.set_password(new_password)
    db.session.commit()
    flash("Password Updated", "success")
    return redirect(url_for("public.logout"))
