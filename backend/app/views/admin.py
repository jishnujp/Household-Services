from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    Blueprint,
)
from sqlalchemy import or_
from app.models import User, ProfessionalDetails, Service, ServiceRequest, Role
from app.utils import login_required
from app import db

admin_view_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_view_bp.route("/home")
@login_required("admin")
def home():
    return render_template(
        "admin/home.html",
        services=Service.query.filter(Service.name != "NoService").all(),
        professionals=ProfessionalDetails.query.all(),
        service_requests=ServiceRequest.query.all(),
    )


@admin_view_bp.route("/add_service", methods=["GET", "POST"])
@login_required("admin")
def add_service():
    if request.method == "POST":
        name = request.form.get("service_name")
        description = request.form.get("service_description")
        base_price = request.form.get("base_price")
        service = Service(name=name, description=description, base_price=base_price)
        db.session.add(service)
        db.session.commit()
        flash("Service added successfully", "success")
        return redirect(url_for("admin.home"))
    elif request.method == "GET":
        return render_template("admin/add_service.html")


@admin_view_bp.route("/approve_professional/<int:id>")
@login_required("admin")
def approve_professional(id):
    professional = ProfessionalDetails.query.get(id)
    professional.is_approved = True
    db.session.commit()
    flash("Professional approved", "success")
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/block_professional/<int:id>")
@login_required("admin")
def block_professional(id):
    professional = ProfessionalDetails.query.get(id)
    professional.is_approved = False
    db.session.add(professional)
    db.session.commit()
    flash("Professional blocked", "success")
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/view_professional/<int:id>")
@login_required("admin")
def view_professional(id):
    professional = ProfessionalDetails.query.get(id)
    return render_template("admin/view_professional.html", professional=professional)


@admin_view_bp.route("/edit_service/<int:id>", methods=["GET", "POST"])
@login_required("admin")
def edit_service(id):
    service = Service.query.get(id)
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


@admin_view_bp.route("/delete_service/<int:id>", methods=["POST"])
@login_required("admin")
def delete_service(id):
    service = Service.query.get(id)
    if not service:
        flash("Service not found.", "error")
        return redirect(url_for("admin.home"))

    noservice = Service.query.filter_by(name="NoService").first()
    if not noservice:
        noservice = Service(
            name="NoService", description="No service selected", base_price=0
        )
        db.session.add(noservice)
        db.session.commit()
    for professional in service.professionals:
        professional.service_id = noservice.id
        professional.is_approved = False
    db.session.commit()

    db.session.delete(service)
    db.session.commit()
    flash("Service deleted successfully", "success")
    return redirect(url_for("admin.home"))


@admin_view_bp.route("/search", methods=["GET", "POST"])
@login_required("admin")
def search():
    if request.method == "POST":
        search_by = request.form.get("search_by")
        search_query = request.form.get("search_query")
        services, professionals, users = [], [], []
        if search_by == "service":
            services = Service.query.filter(
                or_(
                    Service.name.ilike(f"%{search_query}%"),
                    Service.description.ilike(f"%{search_query}%"),
                )
            ).all()

        elif search_by == "professional":
            if search_query.isdigit():
                professionals = (
                    ProfessionalDetails.query.join(User)
                    .filter(
                        or_(
                            User.phone.ilike(f"%{search_query}%"),
                            User.pincode.ilike(f"%{search_query}%"),
                        )
                    )
                    .all()
                )
            else:
                professionals = (
                    ProfessionalDetails.query.join(User)
                    .filter(
                        or_(
                            ProfessionalDetails.username.ilike(f"%{search_query}%"),
                            ProfessionalDetails.description.ilike(f"%{search_query}%"),
                            User.full_name.ilike(f"%{search_query}%"),
                            User.address.ilike(f"%{search_query}%"),
                        )
                    )
                    .all()
                )

        elif search_by == "customer":
            if search_query.isdigit():
                users = User.query.filter(
                    or_(
                        User.phone.ilike(f"%{search_query}%"),
                        User.pincode.ilike(f"%{search_query}%"),
                    )
                ).all()
            else:
                users = User.query.filter(
                    or_(
                        User.full_name.ilike(f"%{search_query}%"),
                        User.username.ilike(f"%{search_query}%"),
                    )
                ).all()
            admin_role = Role.query.filter_by(name="admin").first()
            users = [user for user in users if admin_role not in user.roles]
        else:
            flash("Invalid search criteria", "danger")
            return redirect(url_for("admin.search"))
        if sum([len(services), len(professionals), len(users)]) == 0:
            flash("No results found", "warning")
            return redirect(url_for("admin.search"))
        return render_template(
            "admin/search.html",
            services=services,
            professionals=professionals,
            users=users,
        )
    return render_template("admin/search.html")


@admin_view_bp.route("/summary")
@login_required("admin")
def summary():
    return render_template("admin/summary.html")