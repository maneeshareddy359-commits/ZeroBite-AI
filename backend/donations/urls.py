from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DonationViewSet, PickupRequestViewSet

router = DefaultRouter()
router.register("donations", DonationViewSet, basename="donation")
router.register("pickup-requests", PickupRequestViewSet, basename="pickup-request")

urlpatterns = [
    path("", include(router.urls)),
]
