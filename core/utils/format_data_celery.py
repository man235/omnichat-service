from sop_chat_service.app_connect.models import Room, UserApp
from core import constants


async def celery_format_data_verify_customer(user_app: UserApp, room: Room):
    data = {
        'name': user_app.name,
        'email': user_app.email,
        'facebook_id': user_app.external_id if room.type == constants.FACEBOOK else "",
        'phone': user_app.phone,
        'zalo_id': user_app.external_id if room.type == constants.ZALO else "",
        'type': room.type,
        'avatar': user_app.avatar,
        'page': None,
        'page_url': None,
        'approach_date': None,
        'ip': None,
        'device': None,
        'browser': None,
        "room_id": room.room_id
    }
    return data
