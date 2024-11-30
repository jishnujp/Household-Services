from flask_restful import Api, Resource
from flask import Blueprint, jsonify
from app.models import Service

public_api_bp = Blueprint("api", __name__)

api = Api(public_api_bp)


class GetAvailableServicesResource(Resource):
    def get(self):
        return jsonify(
            [
                {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "base_price": service.base_price,
                    "professionals_count": len(service.professionals),
                }
                for service in Service.query.all()
            ]
        )


api.add_resource(GetAvailableServicesResource, "/get_available_services")
