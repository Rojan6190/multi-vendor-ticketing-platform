import logging

from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Runs for every exception raised inside a DRF view (including ones
    from core/exceptions.py). Converts DRF's default error shape into
    our {status, message, data} envelope. Anything DRF doesn't catch
    becomes a generic logged 500 instead of leaking a traceback.
    """
    response = drf_exception_handler(exc, context)

    if response is not None:
        message = response.data
        if isinstance(message, dict) and "detail" in message and len(message) == 1:
            message = message["detail"]

        response.data = {"status": "error", "message": message, "data": None}
        return response

    logger.exception("Unhandled exception: %s", exc)
    return Response(
        {"status": "error", "message": "Internal server error.", "data": None},
        status=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def custom_404(request, exception=None):
    """Wired into config/urls.py as handler404 — covers URLs DRF never sees."""
    return Response_json({"status": "error", "message": "Not found.", "data": None}, 404)


def custom_500(request):
    """Wired into config/urls.py as handler500."""
    return Response_json({"status": "error", "message": "Internal server error.", "data": None}, 500)


def Response_json(payload, status_code):
    # Plain Django (not DRF) views need a real JsonResponse, not DRF's Response.
    from django.http import JsonResponse
    return JsonResponse(payload, status=status_code)