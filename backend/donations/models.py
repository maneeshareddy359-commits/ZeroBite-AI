from django.conf import settings
from django.db import models
from django.utils import timezone


class Donation(models.Model):
    STATUS = [
        ("available", "Available"),
        ("requested", "Pickup requested"),
        ("collected", "Collected"),
        ("delivered", "Delivered"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    FOOD_TYPES = [
        ("rice", "Rice / Biryani"),
        ("bread", "Bread / Bakery"),
        ("curry", "Curry / Dal"),
        ("vegetables", "Vegetables"),
        ("fruit", "Fruit"),
        ("other", "Other"),
    ]

    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="donations"
    )
    food_name = models.CharField(max_length=120)
    food_type = models.CharField(max_length=20, choices=FOOD_TYPES, default="other")
    quantity_meals = models.PositiveIntegerField()
    prepared_at = models.DateTimeField()
    # Calculated by the AI expiry estimator; never entered by the donor.
    expiry_at = models.DateTimeField()
    pickup_location = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    donor_reliability = models.FloatField(default=0.7)
    demand_level = models.FloatField(default=0.5)
    status = models.CharField(max_length=20, choices=STATUS, default="available")
    ai_score = models.FloatField(null=True, blank=True)
    ai_label = models.CharField(max_length=20, blank=True)
    ai_reason = models.CharField(max_length=255, blank=True)
    ai_expiry_hours = models.FloatField(null=True, blank=True)
    ai_expiry_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "expiry_at"]),
            models.Index(fields=["ai_label", "ai_score"]),
            models.Index(fields=["prepared_at", "food_type"]),
        ]

    @property
    def hours_to_expiry(self):
        return max(0.0, (self.expiry_at - timezone.now()).total_seconds() / 3600)

    def refresh_expiry_status(self):
        if self.expiry_at <= timezone.now() and self.status in ("available", "requested"):
            self.status = "expired"
            self.save(update_fields=["status", "updated_at"])

    def __str__(self):
        return f"{self.food_name} - {self.quantity_meals} meals"


class PickupRequest(models.Model):
    STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("collected", "Collected"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name="pickup_requests")
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pickup_requests")
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
