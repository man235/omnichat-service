from core.schema.base_model import CustomBaseModel
from typing import Optional
from django.utils import timezone
from sop_chat_service.app_connect.models import FanPage, Room, UserApp


ELK_LOG_ACTION = {
    'CHAT': 'chat',
    'HANDLE_MESSAGE': 'handle message from customer',
    'REOPEN': 'reopen',
    'REMIND': 'remind',
    'COMPLETED': 'completed'
}


class ElkCustomer(CustomBaseModel):
    customer_id: Optional[str]
    name: Optional[str]
    from_page: Optional[str]    # page type: livechat, zalo or facebook


class ElkFanpage(CustomBaseModel):
    fanpage_id: Optional[str]
    name: Optional[str]
    

class ElkLogSchema(CustomBaseModel):
    action: str
    user_id: str
    room_id : str
    fanpage: Optional[ElkFanpage]
    customer: Optional[ElkCustomer]
    created_at: Optional[str]


def format_elk_log(
    action: str,
    room: Optional[Room],
    fanpage: Optional[FanPage],
    customer: Optional[UserApp],
) -> ElkLogSchema:
    elk_page = ElkFanpage()
    elk_customer = ElkCustomer()
    
    if fanpage:
        elk_page.name = fanpage.name
        elk_page.fanpage_id = fanpage.page_id
        elk_customer.from_page = fanpage.type
    
    if customer:
        elk_customer.customer_id = customer.external_id
        elk_customer.name = customer.name
    
    doc = ElkLogSchema(
        action=action,
        user_id=room.user_id,
        room_id=room.room_id,
        fanpage=elk_page,
        customer=elk_customer,
        created_at=str(timezone.now())
    )

    return doc
    