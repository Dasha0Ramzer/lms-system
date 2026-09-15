import re
from rest_framework.exceptions import ValidationError


def validate_video_url(value):
    reg = re.compile(
        r'^https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w\-]+'
    )
    if not reg.match(value):
        raise ValidationError("Это не ссылка на 'youtube'")