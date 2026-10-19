from django.utils import timezone
from rest_framework import serializers
from .models import Donation, PickupRequest


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source="donor.get_full_name", read_only=True)
    hours_to_expiry = serializers.FloatField(read_only=True)
    pickup_request_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id", "donor", "donor_name", "food_name", "food_type", "quantity_meals",
            "prepared_at", "expiry_at", "hours_to_expiry", "pickup_location", "notes",
            "status", "ai_score", "ai_label", "ai_reason", "ai_expiry_hours",
            "ai_expiry_reason", "pickup_request_count", "created_at", "updated_at",
        ]
        read_only_fields = [
            "donor", "expiry_at", "status", "ai_score", "ai_label", "ai_reason",
            "ai_expiry_hours", "ai_expiry_reason", "created_at", "updated_at",
            "pickup_request_count",
        ]

    def validate_quantity_meals(self, value):
        if value < 1 or value > 100000:
            raise serializers.ValidationError("Quantity must be between 1 and 100000 meals.")
        return value

    def validate_prepared_at(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Prepared date and time cannot be in the future.")
        return value

    def validate(self, attrs):
        pickup_location = attrs.get("pickup_location")
        if not pickup_location and not (self.instance and self.instance.pickup_location):
            raise serializers.ValidationError({"pickup_location": "Pickup location is required."})
        return attrs


class PickupRequestSerializer(serializers.ModelSerializer):
    requester_name = serializers.CharField(source="requester.get_full_name", read_only=True)
    donation_details = DonationSerializer(source="donation", read_only=True)

    class Meta:
        model = PickupRequest
        fields = [
            "id", "donation", "donation_details", "requester", "requester_name",
            "message", "status", "created_at", "updated_at",
        ]
        read_only_fields = ["requester", "status", "created_at", "updated_at"]
