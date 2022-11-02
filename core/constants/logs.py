TRIGGER_COMPLETED = 'COMPLETED'
TRIGGER_REOPENED = 'REOPENED'
TRIGGER_REMINDED = 'REMINDED'
TRIGGER_LEFT = 'LEFT'
TRIGGER_FORWARDED = 'FORWARDED'

LOG_COMPLETED = '{from_user} have completed the conversation'
LOG_REOPENED = '{from_user} have reopened the conversation'
LOG_REMINDED = '{from_user} has set up remider "{remider}"'
LOG_LEFT = '{from_user} have left the conversation'
LOG_FORWARDED = '{from_user} has forwarded the message to {to_user}'

LOG_MESSAGES = {
    TRIGGER_COMPLETED: LOG_COMPLETED,
    TRIGGER_REOPENED: LOG_REOPENED,
    TRIGGER_REMINDED: LOG_REMINDED,
    TRIGGER_LEFT: LOG_LEFT,
    TRIGGER_FORWARDED: LOG_FORWARDED,
}
