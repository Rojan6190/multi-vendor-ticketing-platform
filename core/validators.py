import re

from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_phone_number(value):
    pattern = r"^\+?[1-9]\d{7,14}$"
    if not re.match(pattern, value):
        raise ValidationError("Enter a valid phone number (E.164 format).")


def validate_future_date(value):
    if value <= timezone.now():
        raise ValidationError("Date must be in the future.")