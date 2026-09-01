import django_filters as filters

from apps.events.models import Event
from core.constants import EventStatus


class EventFilter(filters.FilterSet):
    category = filters.CharFilter(field_name="category__slug")
    city = filters.CharFilter(field_name="venue__city", lookup_expr="iexact")
    start_after = filters.DateTimeFilter(field_name="start_datetime", lookup_expr="gte")
    start_before = filters.DateTimeFilter(field_name="start_datetime", lookup_expr="lte")
    status = filters.ChoiceFilter(choices=EventStatus.choices)

    class Meta:
        model = Event
        fields = ["category", "city", "start_after", "start_before", "status"]