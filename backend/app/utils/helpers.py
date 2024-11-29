from hashlib import md5
from flask import redirect, url_for, abort
from flask_login import current_user
from functools import wraps


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


def role_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("public.login"))
            user_permissions = [urole.name for urole in current_user.roles]
            if role and role not in user_permissions:
                abort(403)

            return f(*args, **kwargs)

        return decorated_function

    return decorator
