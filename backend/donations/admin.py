from django.contrib import admin
from .models import Donation, PickupRequest

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("food_name", "donor", "quantity_meals", "expiry_at", "status", "ai_label", "ai_score")
    list_filter = ("status", "food_type", "ai_label")
    search_fields = ("food_name", "pickup_location", "donor__email")

@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ("donation", "requester", "status", "created_at")
    list_filter = ("status",)
