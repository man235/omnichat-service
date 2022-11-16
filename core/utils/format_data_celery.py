from sop_chat_service.app_connect.models import Room, UserApp
from core import constants


async def celery_format_data_verify_customer(user_app: UserApp, room: Room):
    if room.type == constants.FACEBOOK:
        fanpage_url = f"https://www.facebook.com/profile.php?id={room.page_id.page_id}"
    else:
        fanpage_url = ""
    data = {
        'name': user_app.name,
        'email': user_app.email,
        'facebook_id': user_app.external_id if room.type == constants.FACEBOOK else "",
        'phone': user_app.phone,
        'zalo_id': user_app.external_id if room.type == constants.ZALO else "",
        'type': room.type,
        'avatar': user_app.avatar,
        'fanpage': room.page_id.name,
        'fanpage_url': fanpage_url,
        'approach_date': str(room.created_at.isoformat()),
        "room_id": room.room_id
    }
    return data
