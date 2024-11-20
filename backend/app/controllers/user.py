from flask import current_app as app
from app import db
from sqlalchemy import or_
from app.models import User, Role
from app.controllers.commons import save_image


def create_customer(data: dict):
    existing_user = User.get_user(data["username"])
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


def search_user(**kwargs):
    if kwargs is None:
        return User.query.all()
    if "id" in kwargs:
        return User.query.get(kwargs["id"])
    filters = []
    for key, value in kwargs.items():
        if "__" in key:
            key, op = key.rsplit("__", 1)
        else:
            key, op = key, "eq"
        if hasattr(User, key):
            column = getattr(User, key)
        else:
            raise Exception(f"Invalid key {key}, not found in User")
        if op == "eq":
            filters.append(column == value)
        elif op == "like":
            filters.append(column.like(f"%{value}%"))
        elif op == "in":
            filters.append(column.in_(value))
        elif op == "gt":
            filters.append(column > value)
        elif op == "lt":
            filters.append(column < value)
        elif op == "gte":
            filters.append(column >= value)
        elif op == "lte":
            filters.append(column <= value)
        else:
            raise Exception(f"Invalid operator {op}")

    return User.query.filter(or_(*filters)).all()
