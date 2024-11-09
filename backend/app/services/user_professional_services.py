from hashlib import md5
from flask import current_app as app
from app import db
from app.models import User, Role, ProfessionalDetails, Service


def hash_file_object(file_object):
    hash = md5()
    for chunk in iter(lambda: file_object.read(4096), b""):
        hash.update(chunk)
    # Reset file pointer to the beginning of the file
    file_object.seek(0)
    return hash.hexdigest()


def hash_file(file_path):
    with open(file_path, "rb") as file_object:
        return hash_file_object(file_object)


def is_allowed_file(ext):
    return ext.lower() in app.config["ALLOWED_FILE_EXTENSIONS"]


def is_allowed_image(ext):
    return ext.lower() in app.config["ALLOWED_IMAGE_EXTENSIONS"]


def save_image(file):
    md5_hash = hash_file_object(file)
    ext = file.filename.split(".")[-1]
    if not is_allowed_image(ext):
        raise Exception("Invalid image format")
    file_name = f"{md5_hash}.{ext}"
    file.save(f"{app.root_path}/{app.config['IMAGE_UPLOAD_FOLDER']}/{file_name}")
    return file_name


def save_file(file):
    md5_hash = hash_file_object(file)
    ext = file.filename.split(".")[-1]
    if not is_allowed_file(ext):
        raise Exception("Invalid file format")
    file_name = f"{md5_hash}.{ext}"
    file.save(f"{app.root_path}/{app.config['FILE_UPLOAD_FOLDER']}/{file_name}")
    return file_name


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


def create_professional(data: dict):
    # create professional user
    from pprint import pprint

    pprint(data)
    print(data.keys())
    existing_professional = User.query.filter_by(username=data["username"]).first()
    if existing_professional:
        raise Exception("Professional already exists with this username")

    pdf_file = save_file(data["experience_doc"])
    if Service.query.get(data["service"]) is None:
        raise Exception("Invalid service id")
    professional_details = ProfessionalDetails(
        service_id=data["service"],
        description=data["desc"],
        experience=int(data["experience"]),
        document=pdf_file,
        extra_price=data.get("extra_price", 0),
        is_approved=False,
        username=data["username"],
    )
    db.session.add(professional_details)
    db.session.commit()
    # add user
    data["professional_details"] = professional_details
    data["role"] = [
        Role.query.filter_by(name="professional").first(),
        Role.query.filter_by(name="customer").first(),
    ]
    return create_customer(data)
