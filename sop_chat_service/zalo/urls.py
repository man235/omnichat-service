from django.urls import path
from sop_chat_service.zalo.views import room

app_name = "zalo"
urlpatterns = [
    path("message/<str:room_id>/", view=room, name="room"),

]
