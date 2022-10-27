from typing import Any
from sop_chat_service.app_connect.models import FanPage, Room, UserApp
from django.utils import timezone
from asgiref.sync import sync_to_async
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_oa_follower
from core.schema import NatsChatMessage
import logging
from core import constants
from core.utils.distribute_new_chat import find_user_new_chat

logger = logging.getLogger(__name__)

@sync_to_async
def check_room_zalo(data: NatsChatMessage) -> Room:
    check_fanpage = FanPage.objects.filter(
        page_id=data.recipientId,
        is_active=True,
        type='zalo',
    ).first()
        
    if not check_fanpage:
        logger.debug(f' NOT FIND FROM DATABASE -------------------------')
        return None
    
    user_app = UserApp.objects.filter(
        external_id=data.senderId,
    ).first()

    # print(f"check_room_zalo -------------------------- user_app-{user_app.__dict__}")

    if not user_app:
        logger.debug(f' NOT FIND USER ZALO APP FROM DATABASE ------------------------- ')
        # Find user from zalo oa: Anomynous or Follower
        zalo_app_user: dict = get_oa_follower(
            data.senderId,
            check_fanpage.access_token_page,
        )

        if zalo_app_user.get('message') == 'Success':
            # Follower
            logger.debug(f' ZALO OA`S FOLLOWER USER ------------------------- ')
            zalo_app_user_data: dict = zalo_app_user.get('data')

            # Define user gender
            gender: int = zalo_app_user_data.get('user_gender')
            if gender == 0:
                checked_gender = 'Others'
            elif gender == 1:
                checked_gender = 'Male'
            elif gender == 2:
                checked_gender = 'Female'
            else:
                checked_gender = 'Undefined'

            user_app = UserApp.objects.create(
                external_id = data.senderId,
                name = zalo_app_user_data.get('display_name'),
                avatar = zalo_app_user_data.get('avatar'),
                gender = checked_gender,
            )
        else:
            # Anonymous User
            logger.debug(f' ANONYMOUS USER ZALO ------------------------- ')
            user_app = UserApp.objects.create(
                external_id = data.senderId,
                name = f'Anonymous-{data.senderId}',
            ) 
    
    check_room = Room.objects.filter(
        page_id=check_fanpage, 
        external_id=data.senderId,
        user_id=check_fanpage.user_id,
    ).first()
        
    # user_id=check_fanpage.user_id,
    if not check_room or check_room.completed_date:
        new_room = Room.objects.create(
            page_id = check_fanpage,
            external_id = data.senderId,
            name = user_app.name,
            approved_date = timezone.now(),
            type = "zalo",
            conversation_id = "",
            completed_date = None,
            room_id = f'{check_fanpage.id}{data.senderId}',
            user_id=check_fanpage.user_id,
        )
        return new_room
    else:
        return check_room



async def distribute_new_room_zalo(data: NatsChatMessage) -> Room:
    check_fanpage = FanPage.objects.filter(
        page_id=data.recipientId,
        is_active=True,
        type=constants.ZALO,
    ).first()
        
    if not check_fanpage:
        logger.debug(f' NOT FIND FROM DATABASE -------------------------')
        return None
    
    user_app = UserApp.objects.filter(
        external_id=data.senderId,
    ).first()

    if not user_app:
        logger.debug(f' NOT FIND USER ZALO APP FROM DATABASE ------------------------- ')
        # Find user from zalo oa: Anomynous or Follower
        zalo_app_user: dict = get_oa_follower(
            data.senderId,
            check_fanpage.access_token_page,
        )
            
        if zalo_app_user.get('message') == 'Success':
            # Follower
            logger.debug(f' ZALO OA`S FOLLOWER USER ------------------------- ')
            zalo_app_user_data: dict = zalo_app_user.get('data')
            user_app = UserApp.objects.create(
                external_id = data.senderId,
                name = zalo_app_user_data.get('display_name'),
                avatar = zalo_app_user_data.get('avatar'),
                gender = zalo_app_user_data.get('gender'),
            )
        else:
            # Anonymous User
            logger.debug(f' ANONYMOUS USER ZALO ------------------------- ')
            user_app = UserApp.objects.create(
                external_id = data.senderId,
                name = f'Anonymous-{data.senderId}',
            ) 
    
    check_room = Room.objects.filter(
        page_id=check_fanpage,
        external_id=data.senderId
    )
    # find_admin, find_user = await find_user_new_chat(data.recipientId)
    
    if not check_room:
        find_admin, find_user = await find_user_new_chat(data.recipientId)
        new_room_user = Room.objects.create(
            page_id = check_fanpage,
            external_id = data.senderId,
            name = user_app.name,
            approved_date = timezone.now(),
            type = constants.ZALO,
            conversation_id = "",
            completed_date = None,
            room_id = f'{check_fanpage.id}{data.senderId}',
            user_id=find_user,
        )
        new_room_admin = Room.objects.create(
            page_id = check_fanpage,
            external_id = data.senderId,
            name = user_app.name,
            approved_date = timezone.now(),
            type = constants.ZALO,
            conversation_id = "",
            completed_date = None,
            room_id = f'{check_fanpage.id}{data.senderId}',
            user_id=find_admin,
        )
        check_room = Room.objects.filter(page_id=check_fanpage, external_id=data.senderId)
        return check_room
    else:
        for room_chat in check_room:
            if room_chat.completed_date:
                new_room = Room.objects.create(
                    page_id = check_fanpage,
                    external_id = data.senderId,
                    name = user_app.name,
                    approved_date = timezone.now(),
                    type = constants.ZALO,
                    conversation_id = "",
                    completed_date = None,
                    room_id = f'{check_fanpage.id}{data.senderId}',
                    user_id=check_fanpage.user_id,
                )
                return new_room
        check_room = Room.objects.filter(page_id=check_fanpage, external_id=data.senderId)
        return check_room
