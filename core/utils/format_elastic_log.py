from django.utils import timezone
from sop_chat_service.app_connect.models import Room, UserApp


ELK_LOG_ACTION = {
    'CHAT': 'chat',
    'HANDLE_MESSAGE': 'handle message from customer',
    'REOPEN': 'reopen',
    'REMIND': 'remind',
    'COMPLETED': 'completed'
}


def format_elk_log(
    action: str,
    room_id: str=None,
) -> dict:
    room_qs = Room.objects.filter(room_id=room_id).first()
    userapp_qs = UserApp.objects.filter(external_id=room_qs.external_id).first()
    if room_qs:
        doc = {
            'action': action,
            'user_id': room_qs.user_id,
            'room_id': room_qs.room_id,
            'fanpage': {
                'fanpage_id': room_qs.page_id.page_id,
                'name': room_qs.page_id.name,
            },
            'customer': {
                'customer_id': room_qs.external_id,
                'name': userapp_qs.name if userapp_qs else None
            },
            'created_at': str(timezone.now())
        }
        return doc
    
    return None
    