from hashlib import md5
from flask import current_app as app


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
