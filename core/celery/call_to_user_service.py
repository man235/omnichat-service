import requests
import logging
import time
import asyncio, ujson
from django.conf import settings
from celery import shared_task
from core import constants
from core.stream.redis_connection import redis_client
from core.utils.nats_connect import publish_data_to_nats
from core.utils.format_log_message import format_log_message_from_celery
from typing import Dict
from sop_chat_service.app_connect.models import UserApp, Room

logger = logging.getLogger(__name__)

@shared_task(name = constants.CELERY_TASK_VERIFY_INFORMATION)
def celery_task_verify_information(_data: Dict, *args, **kwargs):
    try:
        headers = {
            'Content-Type': 'application/json'
        }
        url = settings.CUSTOMER_SERVICE_URL + settings.API_VERIFY_INFORMATION
        response = requests.post(url=url, headers=headers, data=ujson.dumps(_data))
        return response.text
    except Exception as e:
        return f"Exception Verify information ERROR: {e}"


@shared_task(name = constants.CELERY_TASK_LOG_MESSAGE_ROOM)
def create_log_time_message(room_id: str):
    room = Room.objects.filter(room_id = room_id).first()
    subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room_id}"
    page_name = room.page_id.name if room.page_id else 'Fchat'
    log_message = format_log_message_from_celery(room.__dict__, f'{constants.LOG_NEW_MESSAGE} to {page_name}', constants.TRIGGER_NEW_MESSAGE)
    asyncio.run(publish_data_to_nats(subject_publish, ujson.dumps(log_message).encode()))
    return "Created Logs Message"


@shared_task(name = constants.COLLECT_LIVECHAT_SOCIAL_PROFILE)
def collect_livechat_social_profile(*args, **kwargs):
    print(" ************************************************************************** ")
    print(kwargs, " ^^^^^^^^^^^^^^^^ ")
    print(kwargs[0])
    print(kwargs[0].get('room_id'))



    room_id = args[0].get('room_id')
    try:
        payload = {
            'type': constants.FCHAT,
            'page': args[0].get('live_chat_id'),
            'ip': args[0].get('client_ip'),
            'device': args[0].get('client_info'),
            'browser': args[0].get('client_info'),
            "room_id": args[0].get('room_id')
        }
        redis_client.set(f'{constants.COLLECT_LIVECHAT_SOCIAL_PROFILE}__{room_id}', ujson.dumps(payload))
        return payload
    except Exception as e:
        return f"Exception Verify information ERROR: {e}"
