from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter
from sop_chat_service.app_connect.api.room_views import RoomViewSet
from sop_chat_service.facebook.api.facebook_auth_view import FacebookViewSet
from sop_chat_service.app_connect.api.message_facebook_views import MessageFacebookViewSet
from sop_chat_service.app_connect.api.label_views import LabelViewSet
from sop_chat_service.app_connect.api.reminder_views import ReminderViewSet
from sop_chat_service.app_connect.api.page_views import PageViewSet
from sop_chat_service.live_chat.api.live_chat_no_auth_views import ChatViewSet
from sop_chat_service.live_chat.api.views import LiveChatViewSet
from sop_chat_service.users.api.views import UserViewSet
from sop_chat_service.zalo.api.zalo_auth_view import ZaloViewSet
from sop_chat_service.zalo.api.zalo_chat_view import ZaloChatViewSet
# from sop_chat_service.facebook.api.facebook_views import FacebookViewSet


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register('rooms', RoomViewSet)
router.register('facebook', FacebookViewSet)
router.register('message', MessageFacebookViewSet)
router.register('label', LabelViewSet)
router.register('reminder', ReminderViewSet)
router.register('live-chat',LiveChatViewSet)
router.register('zalo', ZaloViewSet)
router.register('zalo/message', ZaloChatViewSet)
router.register("chat", ChatViewSet)
router.register("page", PageViewSet)

app_name = "api"
urlpatterns = router.urls
