from django.conf.global_settings import (
    DATETIME_INPUT_FORMATS,
    TIME_INPUT_FORMATS,
)

DATETIME_INPUT_FORMATS.insert(
    0,
    '%Y-%m-%d %I:%M %p',     # 2026-10-25 01:30 PM
)
TIME_INPUT_FORMATS.insert(
    0,
    '%I:%M %p',     # '01:30 PM'
)
