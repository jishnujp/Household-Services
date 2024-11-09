from app import create_app
import os

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        from app.models import User, Role

        Role.create_default_roles()
        User.create_admin_user()

    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
