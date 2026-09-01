from django.core.cache import cache
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from core.mixins import APIResponseMixin
from core.caching import build_cache_key, bump_version, DEFAULT_TTL
from core.constants import EventStatus, UserRole
from apps.events.models import Event, Category, Venue
from apps.events.serializers import(
    EventListSerializer, EventDetailSerializer, 
    CategorySerializer, VenueSerializer,

)
from apps.events.filters import EventFilter
from apps.events.permissions import IsOrganizerOrReadOnly

CACHE_PREFIX = "events"
# CACHE_TTL = 300

class EventViewSet(APIResponseMixin, viewsets.ModelViewSet):
    permission_classes = [IsOrganizerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EventFilter
    search_fields = ["title", "description"]
    ordering_fields = ["start_datetime", "created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Event.objects.select_related("vendor", "vendor__user", "category", "venue")
        user = self.request.user

        if user.is_authenticated and getattr(user, "role", None) == UserRole.ADMIN:
            return qs

        if user.is_authenticated:
            vendor = getattr(user, "vendor_profile", None)
            if vendor: 
                #vendors see published events + their own drafts
                return qs.filter(Q(status=EventStatus.PUBLISHED) | Q(vendor=vendor))
            return qs.filter(status = EventStatus.PUBLISHED)

    def get_serializer_class(self):
        return EventListSerializer if self.action == "list" else EventDetailSerializer

    def list(self, request, *args, **kwargs):
        key = build_cache_key(CACHE_PREFIX, **request.query_params.dict())
        cached = cache.get(key)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(key, response.data, DEFAULT_TTL)
        return response
    def perform_create(self, serializer):
        serializer.save(vendor=self.request.user.vendor_profile)
        bump_version(CACHE_PREFIX)

    def perform_destroy(self, instance):
        instance.delete() #soft delete, inherited from BaseModel
        bump_version(CACHE_PREFIX)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class VenueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer
    permission_classes = [AllowAny]

    

