from django.urls import path
from core.websocket import FacebookChatConsumer
from core.websocket.live_chat_socket import ChatConsumer
from core.websocket.live_chat_socket_saleman import SaleChatConsumer
# from core.websocket import RedisFacebookChatConsumer

websocket_urlpatterns = [
    path("<topic>/<room_id>", FacebookChatConsumer.as_asgi()),
    path("live-chat/<topic>/<room_id>", ChatConsumer.as_asgi()),
    path("chat", SaleChatConsumer.as_asgi())    
]
