from django.urls import path

from . import consumers
print("----------------------------------")
websocket_urlpatterns = [
    path('ws/chat/<room_name>', consumers.ChatConsumer.as_asgi()),
]
