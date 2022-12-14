from os.path import splitext
import os
from storages.backends.s3boto3 import S3Boto3Storage
from os.path import splitext
from django.conf import settings
import uuid
import logging

logger = logging.getLogger(__name__)


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    default_acl = "public-read"


class MediaRootS3Boto3Storage(S3Boto3Storage):
    # location = ''
    file_overwrite = True
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME



def upload_image_to(instance, filename):
    basename, extension = splitext(filename)
    return f'{uuid.uuid4().hex}{extension}'


def upload_file_to_minio(file, room_id, path_minio):
    basename, extension = splitext(file.name)
    file_directory_within_bucket = f'{path_minio}_{room_id}'
    name = f"{uuid.uuid4().hex}{extension}"
    file_path_within_bucket = os.path.join(
        file_directory_within_bucket,
        # file.name
        name
    )
    media_storage = MediaRootS3Boto3Storage()

    if not media_storage.exists(file_path_within_bucket): # avoid overwriting existing file
        media_storage.save(file_path_within_bucket, file)
        file_url = media_storage.url(file_path_within_bucket)
        logger.debug(f"DIR OF MEDIA_STORAGE: ------------------------------ {dir(media_storage)}")
        # data = {
        #     'name': file.name,
        #     'file_url': f"{file_directory_within_bucket}/{name}",
        # }
        return name
