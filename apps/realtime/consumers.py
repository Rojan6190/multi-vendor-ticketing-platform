from channels.generic.websocket import AsyncJsonWebsocketConsumer


class SeatAvailabilityConsumer(AsyncJsonWebsocketConsumer):
    """
    One "room" per event (grouped by slug — same identifier used
    everywhere else in the app). Clients connect to watch an event's
    seats; the server pushes updates whenever tickets/services.py
    locks, releases, or sells a seat.
    """

    async def connect(self):
        self.event_slug = self.scope["url_route"]["kwargs"]["event_slug"]
        self.group_name = f"event_{self.event_slug}_seats"

        if self.scope["user"].is_anonymous:
            await self.close(code=4001)  # must be logged in to watch checkout state
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        pass  # read-only feed for now — no client -> server messages yet

    # "type": "seat_update" in group_send maps to this method name
    async def seat_update(self, event):
        await self.send_json(event["payload"])