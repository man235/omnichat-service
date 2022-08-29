from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AppConnectConfig(AppConfig):
    name = "sop_chat_service.app_connect"
    verbose_name = _("AppConnect")
