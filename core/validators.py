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



#kyc related validators
def validate_file_size(value):
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File too large. Max size is {max_size_mb}MB.")

def validate_document_file(value):
    allowed_extensions = [".pdf", ".jpg", ".jpeg", ".png"]
    ext = "." + value.name.rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f"Unsupported file type '{ext}'. Allowed: {', '.join(allowed_extensions)}")