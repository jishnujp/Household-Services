from flask import current_app as app
from app import db
from app.models import User, Role, ProfessionalDetails, Service
from app.controllers.commons import save_file


def create_professional(data: dict):
    from app.controllers.user import create_customer

    existing_professional = User.query.filter_by(username=data["username"]).first()
    if existing_professional:
        raise Exception("Professional already exists with this username")

    pdf_file = save_file(data["experience_doc"])
    if Service.query.get(data["service"]) is None:
        raise Exception("Invalid service id")
    # add user
    data["role"] = [
        Role.query.filter_by(name="professional").first(),
        Role.query.filter_by(name="customer").first(),
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
        is_approved=False,
    )
    db.session.add(professional_details)
    db.session.commit()
    return professional_details
