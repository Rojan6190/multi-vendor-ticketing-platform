from django.contrib import admin
from apps.events.models import Event, Category, Venue

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "city")
    search_fields = ("name", "city")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "vendor", "status", "start_datetime")
    list_filter = ("status", "category")
    search_fields = ("title",)