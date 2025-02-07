from flask import current_app as app
from sqlalchemy import or_
from app import db
from app.models import User, Role, ProfessionalDetails, Service
from app.controllers.commons import save_file
from app.utils.constants import AllowableRoles


def create_professional(data: dict):
    from app.controllers.user import create_customer

    existing_professional = User.get_user(data["username"])
    if existing_professional:
        raise Exception("Professional already exists with this username")

    pdf_file = save_file(data["experience_doc"])
    if Service.query.get(data["service"]) is None:
        raise Exception("Invalid service id")
    # add user
    data["role"] = [
        Role.query.filter_by(name=AllowableRoles.PROFESSIONAL).first(),
        Role.query.filter_by(name=AllowableRoles.CUSTOMER).first(),
    ]
    new_user = create_customer(data)
    professional_details = ProfessionalDetails(
        id=new_user.id,
        service_id=data["service"],
        business_name=data["business_name"],
        description=data["desc"],
        experience=int(data["experience"]),
        document=pdf_file,
        extra_price=data.get("extra_price", 0),
        is_deactivated=True,
    )
    db.session.add(professional_details)
    db.session.commit()
    return professional_details


# Read
def search_professional(with_deactivated=False, **kwargs):
    if kwargs is None:
        return ProfessionalDetails.query.with_deactivated(with_deactivated).all()
    if "id" in kwargs:
        return ProfessionalDetails.query.with_deactivated(with_deactivated).get(
            kwargs["id"]
        )
    filters = []
    join = False
    for key, value in kwargs.items():
        if "__" in key:
            key, op = key.rsplit("__", 1)
        else:
            key, op = key, "eq"
        if hasattr(ProfessionalDetails, key):
            column = getattr(ProfessionalDetails, key)
        elif hasattr(User, key):
            join = True
            column = getattr(User, key)
        else:
            raise Exception(
                f"Invalid key {key}, not found in ProfessionalDetails or User"
            )
        if op == "eq":
            print(column, value)
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

    if join:
        return (
            ProfessionalDetails.query.with_deactivated(with_deactivated)
            .join(User)
            .filter(or_(*filters))
            .all()
        )
    else:
        return (
            ProfessionalDetails.query.with_deactivated(with_deactivated)
            .filter(or_(*filters))
            .all()
        )


def activate_professional(id: int):
    try:
        professional = ProfessionalDetails.query.with_deactivated().get(id)
        if professional.service.is_deactivated:
            return False, "Service is not activate, activate it first."

        professional.activate()
        return True, "Professional approved"
    except Exception as e:
        print("Error in activating professional", e)
        return False, "Error in activating professional"


def update_professional(id: int, data: dict):
    from app.controllers.user import update_user

    professional = ProfessionalDetails.query.get(id)
    user = update_user(id, data)
    if "document" in data:
        pdf_file = save_file(data["document"])
        professional.document = pdf_file
        data["document"] = pdf_file
        data["is_deactivated"] = True

    if "service_id" in data and professional.service_id != data["service_id"]:
        data["is_deactivated"] = True
    if "experience" in data and professional.experience != data["experience"]:
        data["is_deactivated"] = True

    for key, value in data.items():
        print("_" * 50)
        print(key, value)
        print("_" * 50)

        if key in ["business_name", "avg_rating", "service"]:
            continue
        if key in ["experience", "extra_price"]:
            value = int(value)
        if hasattr(professional, key):
            setattr(professional, key, value)
    db.session.commit()
    return professional
