from .base import BaseHandler
from core import constants

class FacebookHandle(BaseHandler):
    htype: str = constants.FACEBOOK

    async def handle_message(self, *args, **kwargs):
        print("FacebookHandle handle_message: ----------------------+--------= ")
        
