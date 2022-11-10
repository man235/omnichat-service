# from .base import BaseWebSocketHandler
from sop_chat_service.zalo.utils.api_suport.api_zalo_caller import get_oa_follower
from sop_chat_service.app_connect.models import UserApp
from core.schema import NatsChatMessage
from core.handlers import BaseHandler
from core import constants
import logging

logger = logging.getLogger(__name__)


class ActionFollowHandler(BaseHandler):
    send_message_type: str = constants.ACTION_FOLLOW_HANDLER

    async def handle_message(self, room, data: NatsChatMessage, *args, **kwargs):
        user_app = UserApp.objects.filter(
            external_id=data.senderId,
        ).first()
        if user_app:
            zalo_app_user: dict = get_oa_follower(
                data.senderId,
                room.page_id.access_token_page,
            )
            zalo_app_user_data: dict = zalo_app_user.get('data')
            user_app.external_id = None
            user_app.name = zalo_app_user_data.get('display_name')
            user_app.avatar = zalo_app_user_data.get('avatar')
            user_app.email = None
            user_app.phone = None
            user_app.gender = zalo_app_user_data.get('gender')
            user_app.save()
        else:
            return
        logger.debug(f"Action Follow Handler with Customer have id ------ {data.senderId}")
