import uuid
from django.utils.text import slugify


def generate_unique_slug(instance, value, slug_field="slug"):
    """
    Builds a URL-safe slug for `instance`, appending a short random
    suffix on collision instead of letting a duplicate slug crash the save.
    """
    base_slug = slugify(value)
    slug = base_slug
    model_class = instance.__class__

    while model_class.all_objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():  #used all_object instead, (not reusing slugs)
        slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

    return slug