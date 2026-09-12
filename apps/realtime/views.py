from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.mixins import APIResponseMixin
from apps.realtime.services import issue_ws_ticket

class WSTicketView(APIResponseMixin, APIView):
    """
    POST /api/v1/realtime/ws-ticket/ — authenticated (real JWT, normal
    Authorization header) exchange for a short-lived one-time ticket to
    use in the WebSocket URL instead of the real access token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ticket = issue_ws_ticket(request.user)
        return self.success({"ticket": ticket, "expires_in": 30}, "WebSocket ticket issued.")
