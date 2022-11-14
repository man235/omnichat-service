from sop_chat_service.app_connect.models import Room


def block_admin_room(room: Room, user_id: str):
    if room.admin_room_id == user_id:
        room.user_id = user_id
        room.admin_room_id = None
        room.save()
    elif room.user_id == user_id:
        room.user_id = user_id
        room.block_admin = True
        room.save()