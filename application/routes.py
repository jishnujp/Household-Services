from main import app
from flask import render_template, request, redirect, url_for, flash, session, abort
from application.models import *
from functools import wraps
from application.utils import hash_file_object
from datetime import datetime


# login required decorator for admin, customer and professional
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("login"))

            user_id = session["user"]

            user_permissions = [urole.name for urole in User.query.get(user_id).roles]
            if role and role not in user_permissions:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        messages = []
        username = request.form.get("username")
        password = request.form.get("password")
        chosen_role = request.form.get("role")
        if not username:
            messages.append("Username is required")
        if not password:
            messages.append("Password is required")
        user = User.query.filter_by(username=username).first()
        if not user:
            messages.append("User not found")
        elif user and user.password != password:
            messages.append("Incorrect password")
        elif (
            user
            and user.password == password
            and chosen_role not in [role.name for role in user.roles]
        ):

            messages.append("You are not authorized to access this role")
        if messages:
            for message in messages:
                flash(message, "danger")
            return redirect(url_for("login"))

        if user and user.password == password:
            session["user"] = user.id
            session["role"] = chosen_role
            flash("Login successful", "success")
            return redirect(url_for(f"{chosen_role}_home"))
        else:
            flash("Login failed", "danger")
            return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("login.html")


@app.route("/logout")
@login_required()
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("index"))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    if role not in ["customer", "professional"]:
        flash(f"Invalid role: {role}", "danger")
        return redirect(url_for("register", role="customer"))
    messages = []
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        cpassword = request.form.get("cpassword")
        if not username:
            messages.append("Username is required")
        if not password:
            messages.append("Password is required")
        if not cpassword:
            messages.append("Confirm password is required")
        if password and cpassword and password != cpassword:
            messages.append("Passwords do not match")
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            messages.append("Username already exists, choose a differnt one")
        if messages:
            for message in messages:
                flash(message, "danger")
            return redirect(url_for("register", role=role))
        full_name = request.form.get("full_name")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        phone = request.form.get("phone")
        profile_pic = request.files.get("profile_pic")
        if profile_pic:
            # get the md5 hash of the file, to avoid duplicate file names
            md5_hash = hash_file_object(profile_pic)
            profile_name = (
                f"storage/profile_pics/{md5_hash}.{profile_pic.filename.split('.')[-1]}"
            )
            profile_location = url_for("static", filename=profile_name)
            profile_pic.save(f"{app.root_path}{profile_location}")
        else:
            profile_name = None
        if role == "customer":
            user_role = [Role.query.filter_by(name="customer").first()]
        elif role == "professional":
            user_role = [
                Role.query.filter_by(name="professional").first(),
                Role.query.filter_by(name="customer").first(),
            ]
        if role == "professional":
            service_id = request.form.get("service")
            description = request.form.get("desc")
            experience = request.form.get("experience")
            document = request.files.get("experience_doc")
            if document:
                md5_hash = hash_file_object(document)
                pdf_file_name = (
                    f"storage/documents/{md5_hash}.{document.filename.split('.')[-1]}"
                )
                document_path = url_for("static", filename=pdf_file_name)
                document.save(f"{app.root_path}{document_path}")
            else:
                document_path = None
            professional_details = ProfessionalDetails(
                service_id=service_id,
                description=description,
                experience=int(experience),
                document=pdf_file_name,
            )
            db.session.add(professional_details)
            user = User(
                username=username,
                password=password,
                full_name=full_name,
                address=address,
                pincode=pincode,
                phone=phone,
                profile_pic=profile_name,
                roles=user_role,
                professional_details=professional_details,
            )
        else:
            user = User(
                username=username,
                password=password,
                full_name=full_name,
                address=address,
                pincode=pincode,
                phone=phone,
                profile_pic=profile_name,
                roles=user_role,
            )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful", "success")
        return redirect(url_for("login"))

    elif request.method == "GET":
        if role == "professional":
            services = Service.query.filter(Service.name != "NoService").all()
            return render_template(
                "register.html", role=role, available_services=services
            )
        return render_template("register.html", role=role)


@app.route("/admin/home")
@login_required("admin")
def admin_home():
    return render_template(
        "admin/home.html",
        services=Service.query.filter(Service.name != "NoService").all(),
        professionals=ProfessionalDetails.query.all(),
        service_requests=ServiceRequest.query.all(),
    )


@app.route("/admin/add_service", methods=["GET", "POST"])
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
        return redirect(url_for("admin_home"))
    elif request.method == "GET":
        return render_template("admin/add_service.html")


@app.route("/admin/approve_professional/<int:id>")
@login_required("admin")
def approve_professional(id):
    professional = ProfessionalDetails.query.get(id)
    professional.is_approved = True
    db.session.commit()
    flash("Professional approved", "success")
    return redirect(url_for("admin_home"))


@app.route("/admin/block_professional/<int:id>")
@login_required("admin")
def block_professional(id):
    professional = ProfessionalDetails.query.get(id)
    professional.is_approved = False
    db.session.add(professional)
    db.session.commit()
    flash("Professional blocked", "success")
    return redirect(url_for("admin_home"))


@app.route("/admin/view_professional/<int:id>")
@login_required("admin")
def view_professional(id):
    professional = ProfessionalDetails.query.get(id)
    return render_template("admin/view_professional.html", professional=professional)


@app.route("/admin/edit_service/<int:id>", methods=["GET", "POST"])
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
        return redirect(url_for("admin_home"))
    elif request.method == "GET":
        return render_template("admin/add_service.html", service=service)


@app.route("/admin/delete_service/<int:id>", methods=["POST"])
@login_required("admin")
def delete_service(id):
    service = Service.query.get(id)
    if not service:
        flash("Service not found.", "error")
        return redirect(url_for("admin_home"))

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
    return redirect(url_for("admin_home"))


@app.route("/admin/search")
@login_required("admin")
def admin_search():
    return render_template("admin/search.html")


@app.route("/admin/summary")
@login_required("admin")
def admin_summary():
    return render_template("admin/summary.html")


@app.route("/customer/home", methods=["GET"])
@login_required("customer")
def customer_home():
    service_id = request.args.get("service")
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
        )
    all_service = Service.query.filter(Service.name != "NoService").all()
    return render_template("customer/home.html", services=all_service)


@app.route("/customer/search")
@login_required("customer")
def customer_search():
    return render_template("customer/search.html")


@app.route("/customer/summary")
@login_required("customer")
def customer_summary():
    return render_template("customer/summary.html")


@app.route("/customer/book/<int:id>", methods=["GET", "POST"])
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
        return redirect(url_for("customer_home"))
    elif request.method == "GET":
        return render_template("customer/book.html", professional=professional)


@app.route("/professional/home")
@login_required("professional")
def professional_home():
    return render_template("professional/home.html")


@app.route("/professional/search")
@login_required("professional")
def professional_search():
    return render_template("professional/search.html")


@app.route("/professional/summary")
@login_required("professional")
def professional_summary():
    return render_template("professional/summary.html")


@app.route("/home")
def public_home():
    return render_template("home.html")


@app.route("/search")
def public_search():
    return render_template("search.html")


@app.route("/summary")
def public_summary():
    return render_template("summary.html")
