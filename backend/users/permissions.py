from rest_framework.permissions import BasePermission

class IsRole(BasePermission):
    allowed_roles = ()
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role in self.allowed_roles)

class IsDonor(IsRole):
    allowed_roles = ("donor",)

class IsPickupPartner(IsRole):
    allowed_roles = ("ngo", "volunteer")
