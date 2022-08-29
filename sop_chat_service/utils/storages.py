from os.path import splitext


def upload_image_to(instance, filename):
    import uuid
    basename, extension = splitext(filename)
    return f'{uuid.uuid4().hex}{extension}'
