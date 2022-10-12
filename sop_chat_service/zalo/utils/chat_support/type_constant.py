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
