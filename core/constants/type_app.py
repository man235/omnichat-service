FACEBOOK = "facebook"
ZALO = "zalo"
LIVECHAT = "livechat"

ZALO_ROOM_MINIO = "zalo_room"
LIVECHAT_ROOM_MINIO = "livechat_room"

MESSAGE_TEXT = "text"
MESSAGE_EMOJI = "emoji"
MESSAGE_LOG = "message_log"
ACTION_FOLLOW = 'follow'

MESSAGE_LOG_MANAGER = "message_log-manager"
MESSAGE_LOG_STORAGE_DATABASE = 'message_log-storage'
MESSAGE_LOG_WEBSOCKET = 'message_log-websocket'
MESSAGE_LEAVE_LIVECHAT_LOG = "leave-livechat-log"

ACTION_FOLLOW_MANAGER = 'action-follow-manager'
ACTION_FOLLOW_HANDLER = 'action-follow-handler'

WEBSOCKET_MANAGER = "websocket-manager"

STORAGE_MANAGER = "storage-manager"
STORAGE_DATABASE = 'storage-database'
STORAGE_REDIS = 'storage-redis'


SEND_MESSAGE_MANAGER = "send_message-manager"
SEND_MESSAGE_STATUS = "send_message-status"
SEND_MESSAGE_STORAGE_DATABASE = 'send_message-storage'
SEND_MESSAGE_WEBSOCKET = 'send_message-websocket'


REDIS_CONFIG_LIVECHAT = "live_chat-configs"
LIVECHAT_NEW_MESSAGE = "live_chat_new_message"
LIVECHAT_NEW_MESSAGE_ACK = "live_chat_new_message_ack"


SIO_EVENT_NEW_MSG_CUSTOMER_TO_SALEMAN = 'Customer.To.SaleMan'
SIO_EVENT_ACK_MSG_CUSTOMER_TO_SALEMAN = 'Customer.To.SaleMan.ACK'

SIO_EVENT_NEW_MSG_SALEMAN_TO_CUSTOMER = 'SaleMan.To.Customer'
SIO_EVENT_ACK_MSG_SALEMAN_TO_CUSTOMER = 'SaleMan.To.Customer.ACK'


ZALO_DISTRIBUTE_USER_NEW_CHAT = 'Zalo.distribute.user.new.chat'

REMINDER_SALEMAN = "reminder-saleman"
# Log message
LOG_COMPLETED = 'have completed the conversation'
LOG_NEW_MESSAGE = 'new message to'
LOG_REOPENED = 'have reopened the conversation'
LOG_REMINDED = 'has set up reminder'
LOG_LEAVE_LIVECHAT = 'have left the conversation'
LOG_FORWARDED = 'has forwarded the message to'

TRIGGER_NEW_MESSAGE = "new_message"
TRIGGER_COMPLETED = 'completed'
TRIGGER_REOPENED = 'reopen'
TRIGGER_REMINDED = 'reminder'
TRIGGER_LEFT_LEAVE_LIVECHAT = 'leave-livechat'
TRIGGER_FORWARDED = 'forwarded'

LOG_MESSAGE_ACK = 'Log.Message.ACK'

# Status room
ALL='all'
PROCESSING='processing'
COMPLETED = 'completed'
EXPIRED ="expired"