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
        payload = {
            "name": "Thiện Kim",
            "email": "",
            "facebook_id": "5385715904821196",
            "phone": "",
            "zalo_id": "",
            "type": "facebook",
            "avatar": "https://scontent.fhan2-5.fna.fbcdn.net/v/t1.30497-1/84628273_176159830277856_972693363922829312_n.jpg?stp=dst-jpg_p720x720&_nc_cat=1&ccb=1-7&_nc_sid=12b3be&_nc_ohc=rVGEGkZYcO0AX--PdJe&_nc_ht=scontent.fhan2-5.fna&edm=AP4hL3IEAAAA&oh=00_AfDzUy_BjEPkAIn8m-EAbW3fKnewFS8CYYirGZ3hXxxXYQ&oe=63995C59",
            "fanpage": "Thiệnhi",
            "fanpage_url": "https://www.facebook.com/profile.php?id=111462684988462",
            "approach_date": "2022-11-16T09:22:18.222894",
            "room_id": "85385715904821196"
        }
        headers = {
            'Content-Type': 'application/json'
        }
        url = settings.CUSTOMER_SERVICE_URL + settings.API_VERIFY_INFORMATION
        response = requests.post(url=url, headers=headers, data=ujson.dumps(payload))
        print(" *************************************************************************************** ", _data)
        print(response.status_code)
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
