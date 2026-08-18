from core.responses import APIResponse

class APIResponseMixin:
    # Drop into a ViewSet/APIView for self.success()/self.error() shortcuts.

    def success(self, data=None, message="Success", status_code=200):
        return APIResponse.success(data, message, status_code)

    def error(self, message="Something went wrong", data=None, status_code=400):
        return APIResponse.error(message, data, status_code)



class SoftDeleteMixin:
    #DRF calls perform_destroy() on DELETE - route it through soft delete.

    def perform_destroy(self, instance):
        instance.delete()  #BaseModel.delete() soft-deletes by default
