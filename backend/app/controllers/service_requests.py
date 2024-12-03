from sqlalchemy import or_
from app import db
from app.models import User, ProfessionalDetails, ServiceRequest


def create_service_request(
    customer_id, professional_details_id, date_of_service, remarks
):
    try:
        user = User.query.get(customer_id)
        professional = ProfessionalDetails.query.get(professional_details_id)
        # TODO: Check if the professinoal is approved
        if not user or not professional:
            return False, "Invalid customer or professional"
        service_request = ServiceRequest(
            customer_id=customer_id,
            professional_details_id=professional_details_id,
            service_id=professional.service_id,
            date_of_service=date_of_service,
            remarks=remarks,
            professional_details=professional,
            user=user,
        )
        db.session.add(service_request)
        db.session.commit()
        return True, "Service requested successfully"
    except Exception as e:
        db.session.rollback()
        return False, str(e)


def search_service_requests(by=None, **kwargs):
    if kwargs is None:
        return ServiceRequest.query.all()
    if "id" in kwargs:
        return ServiceRequest.query.get(kwargs["id"])
    filters = []
    BY = {"customer": User, "professional": ProfessionalDetails}
    join_table = None
    if by:
        if by not in BY:
            raise Exception(f"Invalid search by {by}")
        join_table = BY[by]
    for key, value in kwargs.items():
        if "__" in key:
            key, op = key.rsplit("__", 1)
        else:
            key, op = key, "eq"
        if hasattr(ServiceRequest, key):
            column = getattr(ServiceRequest, key)
        elif join_table and hasattr(join_table, key):
            column = getattr(join_table, key)
        else:
            print(join_table)
            raise Exception(f"Invalid key {key}, not found in ServiceRequest or {by}")
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

    if join_table:
        return ServiceRequest.query.join(join_table).filter(or_(*filters)).all()
    else:
        return ServiceRequest.query.filter(or_(*filters)).all()


def rate_and_review(service_request_id, data):
    try:
        service_request = ServiceRequest.query.get(service_request_id)
        if not service_request:
            return False, "Service request not found"
        professional = service_request.professional_details
        service_request.rating = data.get("rating")
        service_request.review = data.get("review")
        db.session.commit()
        all_ratings = [
            service_request.rating
            for service_request in ServiceRequest.query.filter_by(
                professional_details_id=professional.id
            ).all()
            if service_request.rating
        ]
        print("ALL rating", all_ratings)
        professional.avg_rating = round(sum(all_ratings) / len(all_ratings), 2)
        db.session.commit()
        return True, "Rated and reviewed successfully"
    except Exception as e:
        db.session.rollback()
        from traceback import print_exc

        print_exc()
