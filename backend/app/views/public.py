from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Blueprint,
    send_from_directory,
    current_app as app,
)
import os
from app.models import User, Service
from app.utils import login_required
from app.controllers import (
    create_customer,
    create_professional,
)


public_view_bp = Blueprint("public", __name__, url_prefix="/")


@public_view_bp.route("/")
def home():
    return render_template("index.html")


@public_view_bp.route("/login", methods=["GET", "POST"])
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
            return redirect(url_for("public.login"))

        if user and user.password == password:
            session["user"] = user.id
            session["role"] = chosen_role
            flash("Login successful", "success")
            return redirect(url_for(f"{chosen_role}.home"))
        else:
            flash("Login failed", "danger")
            return redirect(url_for("public.login"))
    elif request.method == "GET":
        return render_template("login.html")


@public_view_bp.route("/logout")
@login_required()
def logout():
    session.pop("user", None)
    session.pop("role", None)
    return redirect(url_for("public.home"))


@public_view_bp.route("/about")
def about():
    return render_template("about.html")


@public_view_bp.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    if role not in ["customer", "professional"]:
        flash(f"Invalid role: {role}", "danger")
        return redirect(url_for("public.register", role="customer"))
    messages = []
    if request.method == "POST":
        print("Registering")
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
        new_user = None
        data = request.form.to_dict()
        for key in ["profile_pic", "experience_doc"]:
            file = request.files.get(key)
            if file:
                data[key] = file
        if role == "professional":
            new_user = create_professional(data)
        elif role == "customer":
            new_user = create_customer(data)
        if new_user:
            flash("User created successfully", "success")
            return redirect(url_for("public.login"))
        else:
            flash("User creation failed", "danger")
            return redirect(url_for("public.register", role=role))

    elif request.method == "GET":
        if role == "professional":
            services = Service.query.all()
            return render_template(
                "register.html", role=role, available_services=services
            )
        return render_template("register.html", role=role)


@public_view_bp.route("/search")
def search():
    return render_template("search.html")


@public_view_bp.route("/uploads/images/<filename>")
@login_required()
def uploaded_image(filename):
    return send_from_directory(
        os.path.join(app.config["IMAGE_UPLOAD_FOLDER"]),
        filename,
    )


@public_view_bp.route("/uploads/files/<filename>")
@login_required()
def uploaded_file(filename):
    return send_from_directory(
        os.path.join(app.config["FILE_UPLOAD_FOLDER"]),
        filename,
    )
