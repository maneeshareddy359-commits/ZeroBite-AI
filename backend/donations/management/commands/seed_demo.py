from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from donations.models import Donation
from donations.ml_service import process_donation_ai
from ml.expiry_model import predict_expiry_hours

User = get_user_model()


class Command(BaseCommand):
    help = "Create demo accounts and sample donations for presentation."

    def handle(self, *args, **kwargs):
        accounts = [
            ("donor_demo", "donor@example.com", "donor"),
            ("ngo_demo", "ngo@example.com", "ngo"),
            ("volunteer_demo", "volunteer@example.com", "volunteer"),
        ]
        users = {}
        for username, email, role in accounts:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": email, "role": role, "first_name": role.title()},
            )
            user.role = role
            user.email = email
            user.first_name = role.title()
            user.set_password("ZeroBite@123")
            user.save()
            users[role] = user

        if not Donation.objects.exists():
            rows = [
                ("Vegetable Biryani", "rice", 25, 2),
                ("Fresh Bread", "bread", 40, 5),
                ("Mixed Fruit", "fruit", 60, 10),
            ]
            for name, food_type, qty, prepared_hours_ago in rows:
                prepared_at = timezone.now() - timedelta(hours=prepared_hours_ago)
                expiry_hours, _ = predict_expiry_hours(food_type, prepared_at)
                donation = Donation.objects.create(
                    donor=users["donor"],
                    food_name=name,
                    food_type=food_type,
                    quantity_meals=qty,
                    prepared_at=prepared_at,
                    expiry_at=prepared_at + timedelta(hours=expiry_hours),
                    pickup_location="Guntur Community Center",
                    notes="Demo donation",
                )
                process_donation_ai(donation)

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data ready. Password for all demo accounts: ZeroBite@123"
            )
        )
