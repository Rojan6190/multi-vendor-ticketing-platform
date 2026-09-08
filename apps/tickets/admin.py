from django.contrib import admin
from apps.tickets.models import TicketTier, Booking, SeatLock

@admin.register(TicketTier)
class TicketTierAdmin(admin.ModelAdmin):
    list_display = ("event", "name", "price", "total_quantity", "sold_quantity")

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "user", "ticket_tier", "quantity", "status")
    list_filter = ("status",)

admin.site.register(SeatLock)