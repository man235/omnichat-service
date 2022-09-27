from sop_chat_service.app_connect.models import FanPage, Room, UserApp
# from .api_facebook_app import get_user_info
from django.utils import timezone
from asgiref.sync import sync_to_async
import logging
logger = logging.getLogger(__name__)

@sync_to_async
def check_room_zalo(data):
    check_fanpage = FanPage.objects.filter(page_id=data.get("recipientId")).first()
    if not check_fanpage or not check_fanpage.is_active:
        return None
    user_app = UserApp.objects.filter(external_id=data.get("senderId")).first()
    if not user_app:
        logger.debug(f' NOT FIND USER APP FROM ZALO  ------------------------- ')
        res_user_app = get_user_info(data.get("senderId"), check_fanpage.access_token_page)
        if not res_user_app:
            logger.debug(f' NOT FIND USER APP FROM ZALO ------------------------- ')
            return
        user_app = UserApp.objects.create(
            # user_id = res_user_app.get('profile_pic'),
            external_id = data.get("senderId"),
            name = res_user_app.get('last_name') + " " + res_user_app.get('first_name'),
            avatar = res_user_app.get('profile_pic'),
            email = res_user_app.get(''),
            phone = res_user_app.get(''),
            gender = res_user_app.get('gender')
        )
    
    check_room = Room.objects.filter(page_id=check_fanpage.id, external_id=data['senderId'],user_id=check_fanpage.user_id).first()
    if not check_room or check_room.completed_date:
        new_room = Room(
            page_id = check_fanpage,
            external_id = data['senderId'],
            # user_id = data.get("senderId"),        # User SSO
            name = user_app.name,
            approved_date = timezone.now(),
            type = "facebook",
            completed_date = None,
            conversation_id = "",
            room_id = f'{check_fanpage.id}{data.get("senderId")}',
            user_id=check_fanpage.user_id,
        )
        new_room.save()
        return new_room
    else:
        return check_room
