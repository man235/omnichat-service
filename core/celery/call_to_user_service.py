from sop_chat_service.app_connect.models import UserApp, Room
from django.conf import settings
from celery import shared_task
from core import constants
import requests
import time
import logging
logger = logging.getLogger(__name__)


@shared_task(name = constants.CELERY_TASK_VERIFY_INFORMATION)
def celery_task_verify_information(user_app: UserApp, room: Room):
    try:
        payload={
            "name": user_app.name,
            "email": user_app.email,
            "facebook_id": user_app.external_id if room.type == constants.FACEBOOK else "",
            "zalo_id": user_app.external_id if room.type == constants.ZALO else "",
            "type": room.type,
            "room_id": room.room_id
        }
        headers = {
            'Content-Type': 'application/json'
        }
        url = settings.GET_USER_PROFILE_URL + settings.API_VERIFY_INFORMATION
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text
    except Exception as e:
        return f"Exception Create Task Reminder {e}"



@shared_task(name = "collect_livechat_social_profile")
def collect_livechat_social_profile(*args, **kwargs):
    print("collect_livechat_social_profile", args, kwargs)
    return {
        "timestamp": time.time(),
        "**kwargs": kwargs
    }
