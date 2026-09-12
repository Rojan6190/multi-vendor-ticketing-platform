import uuid
from django.db import models
from django.conf import settings

from core.models import BaseModel
from core.constants import BookingStatus
from apps.events.models import Event

class TicketTier(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="ticket_tiers")
    name = models.CharField(max_length=100)
    description = models.TextField(blank= True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_quantity = models.PositiveIntegerField()
    sold_quantity = models.PositiveIntegerField(default=0)
    sales_start = models.DateTimeField(null=True, blank=True)
    sales_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["price"]

    @property
    def available_quantity(self):
        return self.total_quantity - self.sold_quantity

    def __str__(self):
        return f"{self.event.title} - {self.name}"

class SeatLock(BaseModel):
    """
    Temporary hold on N units of a tier during checkout.
    Real Redis + TTL enforcement lands in day 8 - this is just the shape for now.
    """
    ticket_tier = models.ForeignKey(TicketTier, on_delete=models.CASCADE, related_name="locks")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="seat_locks")
    quantity = models.PositiveIntegerField()
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Lock<{self.ticket_tier} x{self.quantity} - {self.user.email}>"

class Booking(BaseModel):  #user's actual booking record
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    ticket_tier = models.ForeignKey(TicketTier, on_delete=models.PROTECT, related_name="bookings")
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)   # snapshot at booking time
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    reference = models.CharField(max_length=20, unique=True, editable=False)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.reference:
            self.reference = uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking<{self.reference}>"