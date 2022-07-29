from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from sop_chat_service.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)


app_name = "api"
urlpatterns = router.urls
