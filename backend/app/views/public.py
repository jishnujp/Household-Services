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
from flask_login import login_user, logout_user, login_required, current_user
import os
from app import login_manager
from app.models import User
from app.controllers import (
    create_customer,
    create_professional,
    search_service,
)
from app.forms import LoginForm
from app.utils.constants import AllowableRoles


public_view_bp = Blueprint("public", __name__, url_prefix="/")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Home route
@public_view_bp.route("/")
def home():
    return render_template("home.html")


# Login route
@public_view_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        messages = []
        username = form.username.data
        password = form.password.data
        chosen_role = form.role.data

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("User not found", "danger")
            return redirect(url_for("public.login"))
        elif user.password != password:
            flash("Incorrect password", "danger")
            return redirect(url_for("public.login"))
        elif user.is_deactivated:
            flash("User is blocked, contact admin", "danger")
            return redirect(url_for("public.login"))
        elif chosen_role not in [role.name for role in user.roles]:
            flash("You are not authorized to access this role", "danger")
            return redirect(url_for("public.login"))

        # Successful login
        login_user(user)
        session["role"] = chosen_role
        flash("Login successful", "success")
        return redirect(url_for(f"{chosen_role}.home"))
    else:
        print("Form not validated")
        print(form.errors)

    return render_template("login.html", form=form)


# Logout route
@public_view_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop("role", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("public.home"))


@public_view_bp.route("/about")
def about():
    return render_template("about.html")


@public_view_bp.route("/register/<role>", methods=["GET", "POST"])
def register(role):
    if role not in [AllowableRoles.CUSTOMER, AllowableRoles.PROFESSIONAL]:
        flash(f"Invalid role: {role}", "danger")
        return redirect(url_for("public.register", role=AllowableRoles.CUSTOMER))
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
        if role == AllowableRoles.PROFESSIONAL:
            new_user = create_professional(data)
        elif role == AllowableRoles.CUSTOMER:
            new_user = create_customer(data)
        if new_user:
            flash("User created successfully", "success")
            return redirect(url_for("public.login"))
        else:
            flash("User creation failed", "danger")
            return redirect(url_for("public.register", role=role))

    elif request.method == "GET":
        if role == AllowableRoles.PROFESSIONAL:
            services = search_service()
            return render_template(
                "register.html", role=role, available_services=services
            )
        return render_template("register.html", role=role)


@public_view_bp.route("/uploads/images/<filename>")
@login_required
def uploaded_image(filename):
    return send_from_directory(
        os.path.join(app.config["IMAGE_UPLOAD_FOLDER"]),
        filename,
    )


@public_view_bp.route("/uploads/files/<filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(
        os.path.join(app.config["FILE_UPLOAD_FOLDER"]),
        filename,
    )
