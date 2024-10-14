from main import app
from flask import render_template, request, redirect, url_for, flash, session
from application.models import *
import os


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
        if messages:
            for message in messages:
                flash(message, "danger")
            return redirect(url_for("login"))

        if user and user.password == password:
            session["user"] = user.id
            flash("Login successful", "success")
            return redirect(url_for(f"{chosen_role}_home"))
        else:
            flash("Login failed", "danger")
            return redirect(url_for("login"))
    elif request.method == "GET":
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
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
            static_location = url_for("static", filename="storage/profile_pics")
            profile_pic_path = (
                f"{app.root_path}{static_location}/{profile_pic.filename}"
            )
            profile_pic.save(profile_pic_path)
        else:
            profile_pic_path = None
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
                static_location = url_for("static", filename="storage/documents")
                document_path = f"{app.root_path}{static_location}/{document.filename}"
                document.save(document_path)
            else:
                document_path = None
            professional_details = ProfessionalDetails(
                service_id=service_id,
                description=description,
                experience=int(experience),
                document=document_path,
            )
            db.session.add(professional_details)
            user = User(
                username=username,
                password=password,
                full_name=full_name,
                address=address,
                pincode=pincode,
                phone=phone,
                profile_pic=profile_pic_path,
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
                profile_pic=profile_pic_path,
                roles=user_role,
            )
        db.session.add(user)
        db.session.commit()
        flash("Registration successful", "success")
        return redirect(url_for("login"))

    elif request.method == "GET":
        if role == "professional":
            services = Service.query.all()
            print(services)
            return render_template(
                "register.html", role=role, available_services=services
            )
        return render_template("register.html", role=role)
