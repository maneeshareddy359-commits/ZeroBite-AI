from pathlib import Path
import sys
from datetime import timedelta

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

from django.db.models import Count, Q

from ml.model import predict
from ml.expiry_model import predict_expiry_hours


def estimate_expiry(food_type, prepared_at):
    """Calculate expiry from food type + prepared time without saving anything."""
    hours, _ = predict_expiry_hours(food_type, prepared_at)
    expiry_at = prepared_at + timedelta(hours=hours)
    food_labels = {
        "rice": "Rice / Biryani",
        "bread": "Bread / Bakery",
        "curry": "Curry / Dal",
        "vegetables": "Vegetables",
        "fruit": "Fruit",
        "other": "Other",
    }
    reason = (
        f"AI estimated a {hours:.1f}-hour rescue window for "
        f"{food_labels.get(food_type, food_type)} from the prepared time."
    )
    return expiry_at, round(hours, 2), reason


def calculate_and_store_expiry(donation):
    expiry_at, hours, reason = estimate_expiry(
        donation.food_type, donation.prepared_at
    )
    donation.expiry_at = expiry_at
    donation.ai_expiry_hours = hours
    donation.ai_expiry_reason = reason
    donation.save(
        update_fields=[
            "expiry_at",
            "ai_expiry_hours",
            "ai_expiry_reason",
            "updated_at",
        ]
    )
    return donation


def _donor_reliability(donation):
    """Estimate reliability from this donor's previous rescue history."""
    Donation = donation.__class__
    previous = Donation.objects.filter(donor=donation.donor).exclude(pk=donation.pk)
    total = previous.count()
    if total == 0:
        return 0.70
    rescued = previous.filter(status__in=("collected", "delivered")).count()
    return round(max(0.40, min(1.00, rescued / total)), 3)


def _current_demand_level(donation):
    """Use current food-type scarcity as a live demand proxy for the ML model."""
    Donation = donation.__class__
    active = Donation.objects.filter(status__in=("available", "requested"))
    total = active.count()
    same_type = active.filter(food_type=donation.food_type).count()
    if total <= 1:
        return 0.75
    scarcity = 1.0 - (same_type / total)
    return round(max(0.35, min(0.95, 0.35 + 0.60 * scarcity)), 3)


def predict_donation(donation):
    """Score the donation using live remaining expiry, donor history and demand."""
    donor_reliability = _donor_reliability(donation)
    demand_level = _current_demand_level(donation)
    payload = {
        "food_type": donation.food_type,
        "quantity_meals": donation.quantity_meals,
        "hours_to_expiry": donation.hours_to_expiry,
        "donor_reliability": donor_reliability,
        "demand_level": demand_level,
    }
    score, label = predict(payload)
    reasons = {
        "CRITICAL": "Very short AI-estimated rescue window and/or strong current demand.",
        "HIGH": "Donation should be prioritized for quick pickup.",
        "MEDIUM": "Donation is useful but has a reasonable rescue window.",
        "LOW": "Donation currently has lower urgency.",
    }
    donation.ai_score = round(score, 2)
    donation.ai_label = label
    donation.ai_reason = (
        f"{reasons[label]} Live factors: {donation.hours_to_expiry:.1f}h left, "
        f"quantity {donation.quantity_meals}, demand {demand_level:.2f}."
    )
    donation.donor_reliability = donor_reliability
    donation.demand_level = demand_level
    donation.save(
        update_fields=[
            "ai_score", "ai_label", "ai_reason",
            "donor_reliability", "demand_level", "updated_at"
        ]
    )
    return donation


def process_donation_ai(donation):
    """Run expiry estimation first, then rescue-priority scoring."""
    calculate_and_store_expiry(donation)
    return predict_donation(donation)
