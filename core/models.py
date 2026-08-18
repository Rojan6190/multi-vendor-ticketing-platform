import uuid
from django.db import models
from django.utils import timezone

from core.managers import BaseManager, AllObjectsManager

class BaseModel(models.Model):

    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable=False  )
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    is_deleted = models.BooleanField(default = False)
    deleted_at = models.DateTimeField(null = True, blank = True)

    objects = BaseManager()
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    
    def delete(self, using = None, keep_parents = False, hard = False ) :
        if hard:
            return super().delete(using=using, keep_parents = keep_parents)

        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields = ["is_deleted ","deleted_at"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted","deleted_at"])

    
        