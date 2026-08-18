from rest_framework.response import Response
from rest_framework import status as http_status

class APIResponse:
    @staticmethod
    def success(data = None, message="Success", status_code=http_status.HTTP_200_OK):
        return Response(
            {"status": "success", "message": message, "data":data},
            status=status_code,
        )

    @staticmethod
    def error(message="Something went wrong", data = None, status_code=http_status.HTTP_400_BAD_REQUEST):
        return Response(
            {"status":"error", "message":message, "data":data},
            status=status_code,
        )