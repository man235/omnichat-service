from asyncio.log import logger
from sop_chat_service.utils.storages import MediaRootS3Boto3Storage
import uuid
import os
import logging


logger = logging.getLogger(__name__)


def upload_file_to_minio_zalo(file, room_id):
    # basename, extension = splitext(file.name)
    extension = file.name.split(".")[-1]
    file_directory_within_bucket = f'zalo_chat_room_{room_id}'
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
        logger.debug(f"DIR OF ZALO MEDIA_STORAGE : ------------------------------ {dir(media_storage)}")
        # data = {
        #     'name': file.name,
        #     'file_url': f"{file_directory_within_bucket}/{name}",
        # }
        return name