from rest_framework.routers import DefaultRouter
from apps.events.views import EventViewSet, CategoryViewSet, VenueViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("venues", VenueViewSet, basename="venue")
router.register("", EventViewSet, basename="event")

urlpatterns = router.urls