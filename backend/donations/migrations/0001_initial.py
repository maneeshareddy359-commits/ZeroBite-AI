# Generated manually for the ZeroBite AI project.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Donation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("food_name", models.CharField(max_length=120)),
                ("food_type", models.CharField(choices=[("rice", "Rice / Biryani"), ("bread", "Bread / Bakery"), ("curry", "Curry / Dal"), ("vegetables", "Vegetables"), ("fruit", "Fruit"), ("other", "Other")], default="other", max_length=20)),
                ("quantity_meals", models.PositiveIntegerField()),
                ("prepared_at", models.DateTimeField()),
                ("expiry_at", models.DateTimeField()),
                ("pickup_location", models.CharField(max_length=255)),
                ("notes", models.TextField(blank=True)),
                ("donor_reliability", models.FloatField(default=0.7)),
                ("demand_level", models.FloatField(default=0.5)),
                ("status", models.CharField(choices=[("available", "Available"), ("requested", "Pickup requested"), ("collected", "Collected"), ("delivered", "Delivered"), ("expired", "Expired"), ("cancelled", "Cancelled")], default="available", max_length=20)),
                ("ai_score", models.FloatField(blank=True, null=True)),
                ("ai_label", models.CharField(blank=True, max_length=20)),
                ("ai_reason", models.CharField(blank=True, max_length=255)),
                ("ai_expiry_hours", models.FloatField(blank=True, null=True)),
                ("ai_expiry_reason", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("donor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="donations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["status", "expiry_at"], name="donations_d_status_4a7c83_idx"),
                    models.Index(fields=["ai_label", "ai_score"], name="donations_d_ai_labe_4f1d8a_idx"),
                    models.Index(fields=["prepared_at", "food_type"], name="donations_d_prepare_1a9e5f_idx"),
                ],
            },
        ),
        migrations.CreateModel(
            name="PickupRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("accepted", "Accepted"), ("collected", "Collected"), ("delivered", "Delivered"), ("cancelled", "Cancelled")], default="pending", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("donation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pickup_requests", to="donations.donation")),
                ("requester", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pickup_requests", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
