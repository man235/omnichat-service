from typing import Any
from sop_chat_service.app_connect.models import FanPage, Room, UserApp
from django.utils import timezone
from asgiref.sync import sync_to_async
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_oa_follower
import logging

logger = logging.getLogger(__name__)

@sync_to_async
def check_room_zalo(data: dict) -> Room:
    # Check fanpage in database models
    check_fanpage = FanPage.objects.filter(
        page_id=data.get('recipientId'),
        is_active=True,
        type='zalo',
    ).first()
    
    if not check_fanpage:
        logger.debug(f' NOT FIND FROM DATABASE -------------------------')
        return None
    
    user_app = UserApp.objects.filter(
        external_id=data.get("senderId"),
    ).first()

    if not user_app:
        logger.debug(f' NOT FIND USER ZALO APP FROM DATABASE ------------------------- ')
        # Find user from zalo oa: Anomynous or Follower
        zalo_app_user: dict = get_oa_follower(
            data.get('senderId'),
            check_fanpage.access_token_page,
        )
            
        if zalo_app_user.get('message') == 'Success':
            # Follower
            logger.debug(f' ZALO OA`S FOLLOWER USER ------------------------- ')
            zalo_app_user_data = zalo_app_user.get('data')
            user_app = UserApp.objects.create(
                external_id = data.get('senderId'),
                name = zalo_app_user_data.get('display_name'),
                avatar = zalo_app_user_data.get('avatar'),
                gender = zalo_app_user_data.get('gender'),
            )
        else:
            # Anonymous User
            logger.debug(f' ANONYMOUS USER ZALO ------------------------- ')
            user_app = UserApp.objects.create(
                external_id = data.get('senderId'),
                name = f'Anonymous-{data.get("senderId")}',
            ) 
    
    check_room = Room.objects.filter(
        page_id=check_fanpage, 
        external_id=data.get('senderId'),
        user_id=check_fanpage.user_id,
    ).first()
        
    # user_id=check_fanpage.user_id,
    if not check_room or check_room.completed_date:
        new_room = Room.objects.create(
            page_id = check_fanpage,
            external_id = data.get('senderId'),
            name = user_app.name,
            approved_date = timezone.now(),
            type = "zalo",
            conversation_id = "",
            completed_date = None,
            room_id = f'{check_fanpage.id}{data.get("senderId")}',
            user_id=check_fanpage.user_id,
        )
        return new_room
    else:
        return check_room
