from application.database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(100))
    profile_pic = db.Column(db.String(20), default='default.jpg')
    pincode = db.Column(db.String(6))
    phone = db.Column(db.String(10))

    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy=True))
    professional_details = db.relationship('ProfessionalDetails', backref='user', lazy=True, uselist=False)
    requested_services = db.relationship('ServiceRequest', backref='user', lazy=True)

class Role(db.Model):
    # admin, customer, professional
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)

class UserRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)   

class ProfessionalDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    document = db.Column(db.String(20), nullable=False)
    extra_price = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    service_requests = db.relationship('ServiceRequest', backref='professional_details', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    base_price = db.Column(db.Integer, nullable=False)

    professionals = db.relationship('ProfessionalDetails', backref='service', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    professional_details_id = db.Column(db.Integer, db.ForeignKey('professional_details.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    date_of_request = db.Column(db.DateTime, nullable=False, default=datetime.now())
    date_of_service = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    remarks = db.Column(db.String(100), nullable=False)


