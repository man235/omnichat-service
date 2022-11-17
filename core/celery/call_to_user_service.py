import requests
import logging
import time
import asyncio, ujson
from django.conf import settings
from celery import shared_task
from core import constants
from core.stream.redis_connection import redis_client
from core.utils.format_elastic_log import format_elk_log
from core.utils.nats_connect import publish_data_to_nats
from core.utils.format_log_message import format_log_message_from_celery
from core.utils.format_message_for_websocket import format_room
from typing import Dict
from sop_chat_service.app_connect.models import Room, UserApp
from elasticsearch import Elasticsearch

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

@shared_task(name = constants.CELERY_TASK_LOG_MESSAGE_REOPEN_ROOM)
def re_open_room(room_id: str):
    room = Room.objects.filter(room_id = room_id).first()
    subject_publish = f"{constants.UPDATE_ROOM_CHAT_SERVICE_TO_WEBSOCKET}.{room_id}"
    page_name = room.page_id.name if room.page_id else None
    log_message = format_room(room.__dict__)
    asyncio.run(publish_data_to_nats(subject_publish, ujson.dumps(log_message).encode()))
    return "Room re_open"


@shared_task(name = constants.COLLECT_LIVECHAT_SOCIAL_PROFILE)
def collect_livechat_social_profile(*args, **kwargs):
    room_id = kwargs.get('room_id')
    try:
        payload = {
            'type': constants.FCHAT,
            'page': kwargs.get('live_chat_id'),
            'ip': kwargs.get('client_ip'),
            'device': kwargs.get('client_info'),
            'browser': kwargs.get('client_info'),
            "room_id": kwargs.get('room_id')
        }
        redis_client.set(f'{constants.COLLECT_LIVECHAT_SOCIAL_PROFILE}__{room_id}', ujson.dumps(payload))
        return payload
    except Exception as e:
        return f"Exception Verify information ERROR: {e}"


@shared_task(name="log_elk")
def log_elk(
    index_pattern: str=settings.ELASTIC_JOURNEY_LOGSTASH,
    action: str=None,
    room_id: str=None,
    *args,
    **kwargs
) -> None:
    try:
        room = Room.objects.filter(room_id=room_id).first()
        
        elk_log = format_elk_log(
            action,
            room, 
            room.page_id, 
            UserApp.objects.filter(external_id=room.external_id).first()
        )
        
        print(f'----here----- {elk_log.__dict__}')
        # Create the client instance
        es = Elasticsearch(
            hosts=[settings.ELASTIC_SEARCH_URL],
            basic_auth=(settings.ELASTIC_USER, settings.ELASTIC_PASSWORD),
        )

        # Log into elastic logstash
        res = es.index(index=index_pattern, document=elk_log.__dict__)
        
        logger.debug(f' RESULT OF LOG ELASTICSEARCH --------- {res} ------------ ')
    except Exception as e:
        logger.debug(f' FAILED TO LOG ELASTICSEARCH --------- {e} -------------- ')
        