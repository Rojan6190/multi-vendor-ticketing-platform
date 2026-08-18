from rest_framework.exceptions import APIException
from rest_framework import status

class BaseAPIException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred."
    default_code = "error"

class NotFoundException(BaseAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "Resource not found."
    default_code =  "not_found"

class PermissionDeniedException(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "You do not have permissions to perform this action."
    default_code = "permission_denied"

class ValidationException(BaseAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Validation failed"
    default_code = "validation_error"

class ConflictException(BaseAPIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict with current state."
    default_code = "conflict"
