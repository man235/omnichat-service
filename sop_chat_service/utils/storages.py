from os.path import splitext
from storages.backends.s3boto3 import S3Boto3Storage
from os.path import splitext


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    file_overwrite = False



def upload_image_to(instance, filename):
    import uuid
    basename, extension = splitext(filename)
    return f'{uuid.uuid4().hex}{extension}'
