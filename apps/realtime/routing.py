from django.urls import re_path
from apps.realtime.consumers import SeatAvailabilityConsumer

websocket_urlpatterns = [
    re_path(r"ws/events/(?P<event_slug>[\w-]+)/seats/$", SeatAvailabilityConsumer.as_asgi()),
]