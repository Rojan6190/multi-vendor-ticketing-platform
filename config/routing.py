from apps.realtime.routing import websocket_urlpatterns as realtime_websocket_urlpatterns

# Root router - just re-exports realtime's patterns for now.
# Other apps can add their own websocket_urlpatterns here later.
websocket_urlpatterns = realtime_websocket_urlpatterns