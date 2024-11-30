from app import create_app, db
from app.config import Config
from app.models import User, Role, Service, ProfessionalDetails
from app.utils.constants import AllowableRoles
import requests
import os


def download_pdf(url, folder, filename=None):
    response = requests.get(url)
    filename = filename or url.split("/")[-1]
    with open(f"{folder}/{filename}", "wb") as file:
        file.write(response.content)
    return filename


def download_image(url, folder, filename=None):
    response = requests.get(url)
    filename = filename or url.split("/")[-1]
    with open(f"{folder}/{filename}", "wb") as file:
        file.write(response.content)
    return filename


# Create sample Services

app = create_app(Config)
with app.app_context():
    from app.models import User, Role

    Role.create_default_roles()
    User.create_admin_user()
app.app_context().push()
services = [
    {
        "name": "Wiring",
        "description": "Installation, maintenance, and repair of electrical systems to ensure safe and reliable power for homes",
        "base_price": 300,
    },
    {
        "name": "Carpentry",
        "description": "Installation, maintenance, and repair of wooden structures to ensure a strong and durable foundation",
        "base_price": 250,
    },
    {
        "name": "Painting",
        "description": "Painting and finishing services to enhance the aesthetic appeal of homes and buildings",
        "base_price": 500,
    },
    {
        "name": "Plumbing",
        "description": "Installation, maintenance, and repair of water and gas systems to ensure proper flow and functionality",
        "base_price": 400,
    },
    {
        "name": "Gardening",
        "description": "Landscaping and maintenance services to create and maintain beautiful outdoor spaces, Charges per hour",
        "base_price": 550,
    },
]

for service in services:
    if Service.query.filter_by(name=service["name"]).first():
        continue
    new_service = Service(
        name=service["name"],
        description=service["description"],
        base_price=service["base_price"],
    )
    db.session.add(new_service)

db.session.commit()


# Create sample Users
professional_role = Role.query.filter_by(name=AllowableRoles.PROFESSIONAL).first()
customer_role = Role.query.filter_by(name=AllowableRoles.CUSTOMER).first()

users = [
    {
        "username": "zeus@gmail.com",
        "password": "Zeus123",
        "full_name": "Zeus Agoraios",
        "address": "Mount Olympus",
        "pincode": "123456",
        "phone": "1234567890",
        "roles": [professional_role, customer_role],
        "profile_pic": "https://easy-peasy.ai/cdn-cgi/image/quality=80,format=auto,width=700/https://fdczvxmwwjwpwbeeqcth.supabase.co/storage/v1/object/public/images/f9ecfab6-a4f7-4ef6-b15f-ef7c082577ab/922fd7c0-e944-4f22-85e5-cfaed6ed27f8.png",
        "professional_details": {
            "service_id": Service.query.filter_by(name="Wiring").first().id,
            "business_name": "Zeus Electricals",
            "description": "Master electrician with 10 years of experience in residential and commercial electrical work",
            "experience": 10,
            "document": "https://mi01000971.schoolwires.net/cms/lib/MI01000971/Centricity/Domain/2059/Greek%20God%20Pantheon.pdf",
            "extra_price": 50,
            "is_deactivated": True,
        },
    },
    {
        "username": "blackadam@gmail.com",
        "password": "BlackAdam123",
        "full_name": "Teth-Adam",
        "address": "Kahndaq",
        "pincode": "543210",
        "phone": "5432109876",
        "roles": [professional_role, customer_role],
        "profile_pic": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRQeL46LK2_AvWPgWmU2IJDV432KECPS9uQkQ&s",
        "professional_details": {
            "service_id": Service.query.filter_by(name="Wiring").first().id,
            "business_name": "Adam Electricals",
            "description": "Powerful electrician with expertise in high-voltage installations and repairs",
            "experience": 7,
            "document": "https://superherojacked.b-cdn.net/wp-content/uploads/2020/08/The-Black-Adam-Workout-PDF.pdf",
            "extra_price": 100,
            "is_deactivated": True,
        },
    },
    {
        "username": "thor@gmail.com",
        "password": "Thor123",
        "full_name": "Thor Odinson",
        "address": "New Asgard, Norway",
        "pincode": "987654",
        "phone": "6789012345",
        "roles": [professional_role, customer_role],
        "profile_pic": "https://w0.peakpx.com/wallpaper/477/401/HD-wallpaper-thor-in-avengers-endgame-thumbnail.jpg",
        "professional_details": {
            "service_id": Service.query.filter_by(name="Carpentry").first().id,
            "business_name": "Hammer Works",
            "description": "God of Thunder with lightning-fast carpentry services for homes and businesses",
            "experience": 5,
            "document": "https://static1.squarespace.com/static/5b0e74d775f9eefeadca6f6e/t/5ee8cd7ed49a18233d7eea62/1592315264865/thor+and+the+giants.pdf",
            "extra_price": 75,
            "is_deactivated": True,
        },
    },
    {
        "username": "carlsen@gmail.com",
        "password": "Carlsen123",
        "full_name": "Magnus Carlsen",
        "address": "Oslo, Norway",
        "pincode": "987654",
        "phone": "6789012345",
        "roles": [customer_role],
        "profile_pic": "https://images.chesscomfiles.com/uploads/v1/master_player/3b0ddf4e-bd82-11e8-9421-af517c2ebfed.f2dc9e34.5000x5000o.41b400498a4b.png",
        "professional_details": None,
    },
]

for user in users:
    if User.query.filter_by(username=user["username"]).first():
        continue

    # download the image and save it in the folder static/storage/profile_pics
    file_name = download_image(
        user["profile_pic"],
        os.path.join(
            app.root_path,
            app.config["IMAGE_UPLOAD_FOLDER"],
        ),
        user["username"].split("@")[0] + ".jpg",
    )
    user["profile_pic"] = file_name

    new_user = User(
        username=user["username"],
        password=user["password"],
        full_name=user["full_name"],
        address=user["address"],
        pincode=user["pincode"],
        phone=user["phone"],
        roles=user["roles"],
        profile_pic=user["profile_pic"],
    )
    db.session.add(new_user)
    db.session.commit()
    # download the pdf and save it in the folder static/storage/documents
    if not user["professional_details"]:
        continue
    file_name = download_pdf(
        user["professional_details"]["document"],
        os.path.join(app.root_path, app.config["FILE_UPLOAD_FOLDER"]),
        user["username"].split("@")[0] + ".pdf",
    )
    user["professional_details"]["document"] = file_name

    if professional_role in user["roles"]:
        professional_details = ProfessionalDetails(
            id=new_user.id,
            service_id=user["professional_details"]["service_id"],
            business_name=user["professional_details"]["business_name"],
            description=user["professional_details"]["description"],
            experience=user["professional_details"]["experience"],
            document=user["professional_details"]["document"],
            extra_price=user["professional_details"]["extra_price"],
            is_deactivated=user["professional_details"]["is_deactivated"],
        )
        db.session.add(professional_details)

db.session.commit()

print("Database populated successfully!")
