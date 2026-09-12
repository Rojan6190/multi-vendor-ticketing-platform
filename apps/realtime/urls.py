from django.urls import path
from apps.realtime.views import WSTicketView

urlpatterns = [
    path("ws-ticket/", WSTicketView.as_view(), name = "ws-ticket"),
]