from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ZeroBite profile", {"fields": ("role", "phone")}),
    )
    list_display = ("username", "email", "role", "is_active", "date_joined")
