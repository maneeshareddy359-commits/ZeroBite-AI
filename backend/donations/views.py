from django.db import transaction
from django.db.models import Q, Count, Sum
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Donation, PickupRequest
from .serializers import DonationSerializer, PickupRequestSerializer
from .ml_service import process_donation_ai, estimate_expiry
from users.permissions import IsPickupPartner

ACTIVE = ("available", "requested")


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        Donation.objects.filter(
            expiry_at__lte=timezone.now(), status__in=ACTIVE
        ).update(status="expired")
        qs = (
            Donation.objects.select_related("donor")
            .annotate(pickup_request_count=Count("pickup_requests"))
            .order_by("-ai_score", "expiry_at")
        )
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(
                Q(food_name__icontains=q)
                | Q(pickup_location__icontains=q)
                | Q(food_type__icontains=q)
            )
        if self.request.query_params.get("active") == "true":
            qs = qs.filter(status__in=ACTIVE)
        if self.action in ["update", "partial_update", "destroy"]:
            qs = qs.filter(donor=self.request.user)
        return qs

    def create(self, request, *args, **kwargs):
        if request.user.role != "donor":
            return Response(
                {"detail": "Only donor accounts can create donations."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                self.perform_create(serializer)
        except Exception as exc:
            # Never expose Django's HTML debug page to the browser.
            return Response(
                {
                    "detail": "AI processing failed. The donation was not saved. "
                    "Please check the food type and prepared date/time and try again.",
                    "code": "AI_PROCESSING_ERROR",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        # expiry_at is required by the database, so calculate it BEFORE the
        # first INSERT. The donor never supplies expiry_at.
        food_type = serializer.validated_data["food_type"]
        prepared_at = serializer.validated_data["prepared_at"]
        expiry_at, expiry_hours, expiry_reason = estimate_expiry(
            food_type, prepared_at
        )

        donation = serializer.save(
            donor=self.request.user,
            expiry_at=expiry_at,
            ai_expiry_hours=expiry_hours,
            ai_expiry_reason=expiry_reason,
        )
        process_donation_ai(donation)

    def perform_update(self, serializer):
        # Recalculate AI expiry whenever prepared time or food type changes.
        data = serializer.validated_data
        food_type = data.get("food_type", serializer.instance.food_type)
        prepared_at = data.get("prepared_at", serializer.instance.prepared_at)
        expiry_at, expiry_hours, expiry_reason = estimate_expiry(
            food_type, prepared_at
        )

        donation = serializer.save(
            expiry_at=expiry_at,
            ai_expiry_hours=expiry_hours,
            ai_expiry_reason=expiry_reason,
        )
        process_donation_ai(donation)

    @action(detail=False, methods=["get"])
    def my(self, request):
        qs = (
            Donation.objects.filter(donor=request.user)
            .annotate(pickup_request_count=Count("pickup_requests"))
            .order_by("-created_at")
        )
        return Response(DonationSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def recommended(self, request):
        qs = (
            Donation.objects.filter(status="available")
            .annotate(pickup_request_count=Count("pickup_requests"))
            .order_by("-ai_score", "expiry_at")[:20]
        )
        return Response(DonationSerializer(qs, many=True).data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = Donation.objects.all()
        active = qs.filter(status__in=ACTIVE)
        rescued = qs.filter(status__in=["collected", "delivered"])
        return Response(
            {
                "total_donations": qs.count(),
                "active_donations": active.count(),
                "rescued_meals": rescued.aggregate(v=Sum("quantity_meals"))["v"] or 0,
                "available_meals": active.aggregate(v=Sum("quantity_meals"))["v"] or 0,
                "critical": active.filter(ai_label="CRITICAL").count(),
                "high": active.filter(ai_label="HIGH").count(),
            }
        )

    @action(detail=True, methods=["post"], permission_classes=[IsPickupPartner])
    def request_pickup(self, request, pk=None):
        donation = self.get_object()
        donation.refresh_expiry_status()
        if donation.status != "available":
            return Response(
                {"detail": "This donation is not currently available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pickup, created = PickupRequest.objects.get_or_create(
            donation=donation,
            requester=request.user,
            defaults={"message": request.data.get("message", "")},
        )
        if not created:
            return Response(PickupRequestSerializer(pickup).data)

        donation.status = "requested"
        donation.save(update_fields=["status", "updated_at"])
        return Response(PickupRequestSerializer(pickup).data, status=status.HTTP_201_CREATED)


class PickupRequestViewSet(viewsets.ModelViewSet):
    serializer_class = PickupRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "donor":
            return PickupRequest.objects.filter(
                donation__donor=user
            ).select_related("donation", "requester")
        return PickupRequest.objects.filter(requester=user).select_related(
            "donation", "requester"
        )

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Use the donation Request pickup action to create a pickup request."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        pickup = self.get_object()
        if request.user.role != "donor" or pickup.donation.donor_id != request.user.id:
            return Response(
                {"detail": "Only the donation owner can accept this request."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if pickup.status != "pending":
            return Response(
                {"detail": "Only pending requests can be accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # A donation has one active pickup at a time. Other pending requests are cancelled.
        PickupRequest.objects.filter(donation=pickup.donation, status="pending").exclude(
            id=pickup.id
        ).update(status="cancelled", updated_at=timezone.now())
        pickup.status = "accepted"
        pickup.save(update_fields=["status", "updated_at"])
        pickup.donation.status = "requested"
        pickup.donation.save(update_fields=["status", "updated_at"])
        return Response(PickupRequestSerializer(pickup).data)

    @action(detail=True, methods=["post"])
    def status(self, request, pk=None):
        pickup = self.get_object()
        new = request.data.get("status")
        if new not in {"accepted", "collected", "delivered", "cancelled"}:
            return Response(
                {"detail": "Invalid pickup status."}, status=status.HTTP_400_BAD_REQUEST
            )

        is_donor = pickup.donation.donor_id == request.user.id
        is_requester = pickup.requester_id == request.user.id
        if not (is_donor or is_requester):
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        if new == "accepted":
            if not is_donor or pickup.status != "pending":
                return Response({"detail": "Only the donor can accept a pending request."}, status=400)
            return self.accept(request, pk)

        if new == "collected" and (not is_requester or pickup.status != "accepted"):
            return Response({"detail": "The pickup must be accepted before collection."}, status=400)
        if new == "delivered" and (not is_requester or pickup.status != "collected"):
            return Response({"detail": "The pickup must be collected before delivery."}, status=400)
        if new == "cancelled" and pickup.status in ("collected", "delivered", "cancelled"):
            return Response({"detail": "This pickup can no longer be cancelled."}, status=400)

        pickup.status = new
        pickup.save(update_fields=["status", "updated_at"])

        if new in ("collected", "delivered"):
            pickup.donation.status = new
            pickup.donation.save(update_fields=["status", "updated_at"])
        elif new == "cancelled":
            other_active = PickupRequest.objects.filter(
                donation=pickup.donation, status__in=["accepted"]
            ).exclude(id=pickup.id).exists()
            if not other_active:
                pickup.donation.status = "available"
                pickup.donation.save(update_fields=["status", "updated_at"])

        return Response(PickupRequestSerializer(pickup).data)
