from flask import current_app as app
from app import db
from app.models import Service


def create_service(data: dict):
    existing_service = Service.query.filter_by(name=data["name"]).first()
    if existing_service:
        raise Exception("Service already exists with this name")
    new_service = Service(
        name=data["service_name"],
        description=data["service_description"],
        base_price=data["base_price"],
    )
    db.session.add(new_service)
    db.session.commit()
    return new_service


def update_service(data: dict):
    service = Service.query.get(data["id"])
    if service is None:
        raise Exception("Service not found")
    service.name = data["service_name"]
    service.description = data["service_description"]
    service.base_price = data["base_price"]
    db.session.commit()
    return service


def delete_service(id: int):
    service = Service.query.get(id)
    if not service:
        raise Exception("Service not found")
    db.session.delete(service)
    db.session.commit()
    return service
