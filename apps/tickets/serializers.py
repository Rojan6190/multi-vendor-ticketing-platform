from rest_framework import serializers
from apps.tickets.models import TicketTier, Booking


class TicketTierSerializer(serializers.ModelSerializer):
    available_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = TicketTier
        fields = ["id", "event", "name", "description", "price", "total_quantity",
                  "sold_quantity", "available_quantity", "sales_start", "sales_end", "created_at"]
        read_only_fields = ["id", "event", "sold_quantity", "created_at"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "user", "ticket_tier", "quantity", "unit_price",
                  "total_amount", "status", "reference", "qr_code", "created_at"]
        read_only_fields = fields


class BookingCreateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)