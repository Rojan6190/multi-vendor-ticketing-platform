from django.utils import timezone
from rest_framework import serializers

from apps.events.models import Event, Category, Venue

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]
        read_only_fields = ["id", "slug"]

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ["id", "name", "address", "city", "latitude", "longitude"]
        read_only_fields = ["id"]

class EventListSerializer(serializers.ModelSerializer):
    #Lightweight - no nested category/venue objects, keeps list payload small
    category = serializers.SlugRelatedField(slug_field = "slug", read_only = True)
    city = serializers.CharField(source="venue.city", read_only=True)
    vendor_name = serializers.CharField(source="vendor.business_name", read_only=True)


    class Meta:
        model = Event
        fields = ["id", "title", "slug", "category", "city", "vendor_name", "start_datetime", "status", "cover_image"]

class EventDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    venue = VenueSerializer(read_only = True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category", queryset=Category.objects.all(), write_only = True
    )
    venue_id = serializers.PrimaryKeyRelatedField(
        source="venue", queryset=Venue.objects.all(), write_only=True
    )

    class Meta:
        model = Event
        fields = ["id", "vendor", "category", "category_id", "venue", "venue_id",
                  "title", "slug", "description", "cover_image",
                  "start_datetime", "end_datetime", "status", "created_at"]
        read_only_fields = ["id", "vendor", "slug", "created_at"]

    def validate(self, attrs):
        start = attrs.get("start_datetime", getattr(self.instance, "start_datetime", None))
        end = attrs.get("end_datetime", getattr(self.instance, "end_datetime", None))
        if start and end and end <= start:
            raise serializers.ValidationError("end_datetime must be after start_datetime. ")
        if self.isinstance is None and start and start <= timezone.now():
            raise serializers.ValidationError("start_datetime must be in the future.")
        return attrs
