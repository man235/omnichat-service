from django.urls import path
from core.websocket import FacebookChatConsumer
# from core.websocket import RedisFacebookChatConsumer

websocket_urlpatterns = [
    path("<topic>/<room_id>", FacebookChatConsumer.as_asgi()),
]
