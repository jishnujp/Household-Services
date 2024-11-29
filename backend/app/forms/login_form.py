from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.utils.constants import AllowableRoles


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(message="Username is required"),
            Email(message="Please enter a valid email address"),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(message="Password is required"),
            Length(min=5, message="Password must be at least 5 characters long"),
        ],
    )
    role = SelectField(
        "Role",
        choices=[(role, role.capitalize()) for role in AllowableRoles.all()],
        default=AllowableRoles.CUSTOMER,
        validators=[DataRequired(message="Role is required")],
    )

    # Custom validation for user role
    def validate_role(self, field):
        if field.data not in AllowableRoles.all():
            raise ValidationError("Invalid role selected")
