from django.urls import path
from core.websocket import FacebookChatConsumer
from core.websocket.live_chat_socket import ChatConsumer
# from core.websocket import RedisFacebookChatConsumer

websocket_urlpatterns = [
    path("<x_auth_user_id>/<topic>/<room_id>", FacebookChatConsumer.as_asgi()),
    path("live-chat/<topic>/<room_id>", ChatConsumer.as_asgi()),
    # path("chat", SaleChatConsumer.as_asgi())    
]
