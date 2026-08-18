from django.db import models

class BaseQuerySet(models.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False)
    
    def dead(self):
        return self.filter(is_deleted=True)
    

class BaseManager(models.Manager):
    """
    Default manager for every model that inherits BaseModel.
    Automatically excludes soft-deleted rows, so `Model.objects.all()`
    never returns deleted data without extra filtering in every view.
    """

    def get_queryset(self):
        return BaseQuerySet(self.model, using=self._db).alive()


class AllObjectsManager(models.Manager):
    """
    Unfiltered manager - sees soft-deleted rows too.
    Use via Model.all_objects, e.g. for an admin 'trash' view
    or restoring a deleted record. Avoid using this in normal app logic.
    """
    def get_queryset(self):
        return BaseQuerySet(self.model, using= self._db)