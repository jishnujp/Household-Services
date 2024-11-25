from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Blueprint,
)
import plotly.express as px
import plotly.io as pio
from app.models import Service, Role, ProfessionalDetails
from app.utils import login_required
from app import db
from app.controllers import (
    search_professional,
    search_user,
    search_service,
    search_service_requests,
    create_service,
    deactivate_service,
    activate_professional,
)

admin_view_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_view_bp.route("/home")
@login_required("admin")
def home():
    return render_template(
        "admin/home.html",
        services=Service.query.with_deactivated().all(),
        professionals=ProfessionalDetails.query.with_deactivated().all(),
        service_requests=search_service_requests(),
    )


@admin_view_bp.route("/add_service", methods=["GET", "POST"])
@login_required("admin")
def add_service():
    if request.method == "POST":
        try:
            create_service(request.form.to_dict())
            flash("Service added successfully", "success")
        except Exception as e:
            from traceback import print_exc

            print_exc()
            flash(f"Error in adding service: {str(e)}", "danger")
        return redirect(url_for("admin.home"))
    elif request.method == "GET":
        return render_template("admin/add_service.html")


@admin_view_bp.route("/approve_professional/<int:id>")
@login_required("admin")
def approve_professional(id):
    stat, msg = activate_professional(id)
    color = "success" if stat else "danger"
    flash(msg, color)
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/block_professional/<int:id>")
@login_required("admin")
def block_professional(id):
    professional = ProfessionalDetails.query.get(id)
    professional.deactivate()
    flash("Professional blocked", "success")
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/view_professional/<int:id>")
@login_required("admin")
def view_professional(id):
    professional = search_professional(id=id)
    return render_template("admin/view_professional.html", professional=professional)


@admin_view_bp.route("/edit_service/<int:id>", methods=["GET", "POST"])
@login_required("admin")
def edit_service(id):
    service = search_service(id=id)
    if request.method == "POST":
        new_name = request.form.get("service_name")
        new_desc = request.form.get("service_description")
        new_base_price = request.form.get("base_price")
        if new_name != service.name:
            service.name = new_name
        if new_desc != service.description:
            service.description = new_desc
        if new_base_price != service.base_price:
            service.base_price = new_base_price

        db.session.commit()
        flash("Service updated successfully", "success")
        return redirect(url_for("admin.home"))
    elif request.method == "GET":
        return render_template("admin/add_service.html", service=service)


@admin_view_bp.route("/deactivate_service/<int:id>", methods=["POST"])
@login_required("admin")
def deactivate_service_view(id):
    try:
        deactivate_service(id)
        flash("Service deactivated successfully", "success")
    except Exception as e:
        print(e)
        flash(f"Error in deactivating service", "danger")
        raise e
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/activate_service/<int:id>", methods=["POST"])
@login_required("admin")
def activate_service(id):
    print("Activating service")
    service = search_service(id=id)
    service.activate()
    flash("Service activated successfully", "success")
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/search", methods=["GET", "POST"])
@login_required("admin")
def search():
    if request.method == "POST":
        search_by = request.form.get("search_by")
        search_query = request.form.get("search_query")
        services, professionals, users, service_requests = [], [], [], []
        if search_by == "service":
            services = search_service(
                name__like=search_query, description__like=search_query
            )

        elif search_by == "professional":
            if search_query.isdigit():
                professionals = search_professional(
                    phone__like=search_query, pincode__like=search_query
                )
            else:
                professionals = search_professional(
                    username__like=search_query,
                    business_name__like=search_query,
                    description__like=search_query,
                    full_name__like=search_query,
                    address__like=search_query,
                )

        elif search_by == "customer":
            if search_query.isdigit():
                users = search_user(
                    phone__like=search_query, pincode__like=search_query
                )
            else:
                users = search_user(
                    username__like=search_query, full_name__like=search_query
                )
            admin_role = Role.query.filter_by(name="admin").first()
            users = [user for user in users if admin_role not in user.roles]
        elif search_by == "service_request":
            service_requests = []
            service_requests += (
                search_service_requests(remarks__like=search_query) or []
            )
            service_requests += (
                search_service_requests(
                    by="customer",
                    address__like=search_query,
                    full_name__like=search_query,
                    username__like=search_query,
                    phone__like=search_query,
                    pincode__like=search_query,
                )
                or []
            )
            service_requests += (
                search_service_requests(
                    by="professional",
                    business_name__like=search_query,
                    description__like=search_query,
                )
                or []
            )

        else:
            flash("Invalid search criteria", "danger")
            return redirect(url_for("admin.search"))
        if (
            sum([len(services), len(professionals), len(users)], len(service_requests))
            == 0
        ):
            flash("No results found", "warning")
            return redirect(url_for("admin.search"))
        return render_template(
            "admin/search.html",
            services=services,
            professionals=professionals,
            users=users,
            service_requests=service_requests,
        )
    return render_template("admin/search.html")


@admin_view_bp.route("/summary")
@login_required("admin")
def summary():
    # get all the customer ratings
    customer_ratings = {i: 0 for i in range(6)}
    all_service_requests = search_service_requests()
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

    # get the status of all service requests and plot a pie chart
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

    # get html of the plots
    rating_plot_html = pio.to_html(rating_fig, full_html=False)
    status_plot_html = pio.to_html(status_fig, full_html=False)
    return render_template(
        "admin/summary.html",
        rating_plot_html=rating_plot_html,
        status_plot_html=status_plot_html,
    )
