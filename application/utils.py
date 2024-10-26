from hashlib import md5


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
