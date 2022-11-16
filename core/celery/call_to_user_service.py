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
def celery_task_verify_information(data: Dict, *args, **kwargs):
    try:
        # payload = {
        #     'name': data.get('name'),
        #     'email': data.get('email'),
        #     'facebook_id': data.get('external_id') if data.get('type') == constants.FACEBOOK else "",
        #     'phone': data.get('phone'),
        #     'zalo_id': data.get('external_id') if data.get('type') == constants.ZALO else "",
        #     'type': data.get('type'),
        #     'avatar': data.get('avatar'),
        #     'page': None,
        #     'page_url': None,
        #     'approach_date': None,
        #     'ip': None,
        #     'device': None,
        #     'browser': None,
        #     "room_id": data.get('room_id')
        # }
        headers = {
            'Content-Type': 'application/json'
        }
        url = settings.CUSTOMER_SERVICE_URL + settings.API_VERIFY_INFORMATION
        response = requests.request("POST", url=url, headers=headers, data=data)
        return response.text
    except Exception as e:
        return f"Exception Verify information ERROR: {e}"


@shared_task(name = constants.CELERY_TASK_LOG_MESSAGE_ROOM)
def create_log_time_message(room_id: str):
    room = Room.objects.filter(room_id = room_id).first()
    subject_publish = f"{constants.CHAT_SERVICE_TO_CORECHAT_PUBLISH}.{room_id}"
    page_name = room.page_id.name if room.page_id else None
    log_message = format_log_message_from_celery(room.__dict__, f'{constants.LOG_SEND_MESSAGE} to {page_name}', constants.TRIGGER_SEND_MESSAGE)
    asyncio.run(publish_data_to_nats(subject_publish, ujson.dumps(log_message).encode()))
    return "Created Logs Message"


@shared_task(name = "collect_livechat_social_profile")
def collect_livechat_social_profile(*args, **kwargs):
    print("collect_livechat_social_profile", args, kwargs)
    try:
        payload = {
            'name': None,
            'email': None,
            'facebook_id': None,
            'phone': None,
            'zalo_id': None,
            'type': constants.FCHAT,
            'avatar': None,
            'page': kwargs.get('live_chat_id'),
            'page_url': None,
            'approach_date': None,
            'ip': kwargs.get('client_ip'),
            'device': kwargs.get('client_info'),
            'browser': kwargs.get('client_info'),
            "room_id": kwargs.get('room_id')
        }
        headers = {
            'Content-Type': 'application/json'
        }
        url = settings.CUSTOMER_SERVICE_URL + settings.API_VERIFY_INFORMATION
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text
    except Exception as e:
        return f"Exception Verify information ERROR: {e}"
