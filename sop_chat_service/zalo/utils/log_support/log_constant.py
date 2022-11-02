
TRIGGER_COMPLETED = 'COMPLETED'
TRIGGER_REOPENED = 'REOPENED'
TRIGGER_REMINDED = 'REMINDED'
TRIGGER_LEFT = 'LEFT'
TRIGGER_FORWARDED = 'FORWARDED'

LOG_MESSAGES = {
    TRIGGER_COMPLETED: '{from_user} have completed the conversation',
    TRIGGER_REOPENED: '{from_user} have reopened the conversation',
    TRIGGER_REMINDED: '{from_user} has set up remider "{remider}"',
    TRIGGER_LEFT: '{from_user} have left the conversation',
    TRIGGER_FORWARDED: '{from_user} has forwarded the message to {to_user}',
}
