from flask import current_app as app
from app import db
from app.models import User, Role
from app.controllers.commons import save_image


def create_customer(data: dict):
    existing_user = User.query.filter_by(username=data["username"]).first()
    if existing_user:
        raise Exception("User already exists with this username")
    profile_pic = data.get("profile_pic")
    if profile_pic:
        profile_name = save_image(profile_pic)
    else:
        profile_name = "default.jpg"

    if len(data.get("role", [])) == 0:
        data["role"] = [Role.query.filter_by(name="customer").first()]

    new_user = User(
        username=data["username"],
        password=data["password"],
        full_name=data.get("full_name"),
        address=data.get("address"),
        pincode=data.get("pincode"),
        phone=data.get("phone"),
        roles=data["role"],
        profile_pic=profile_name,
        professional_details=data.get("professional_details"),
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user
