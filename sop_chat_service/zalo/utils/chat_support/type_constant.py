# ----- TYPES OF MESSAGE -----
from dataclasses import dataclass


TEXT_MESSAGE = 'text'
FILE_MESSAGE = 'file'
IMAGE_MESSAGE = 'image'
STICKER_MESSAGE = 'sticker'
GIF_MESSAGE = 'gif'
VOICE_MESSAGE = 'voice'
VIDEO_MESSAGE = 'video'
AUDIO_MESSAGE = 'audio'
LOCATION_MESSAGE = 'location'
LINK_MESSAGE = 'link'

ATTACHMENT_MESSAGE = (
    FILE_MESSAGE,
    IMAGE_MESSAGE,
    STICKER_MESSAGE,
    GIF_MESSAGE,
)

FILE_CONTENT_TYPE = 'application'
FILE_CONTENT_TYPE_TEXT = 'text'
FILE_MSWORD_EXTENSION = 'msword'
FILE_DOC_EXTENSION = 'doc', 'docx'
FILE_PDF_TYPE = 'pdf'
FILE_CSV_TYPE = 'csv'

SUPPORTED_FILE_EXTENSION_ZALO = ('pdf, doc, docx, csv')