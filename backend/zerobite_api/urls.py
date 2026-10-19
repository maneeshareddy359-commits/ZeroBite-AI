from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection

def health(request):
    with connection.cursor() as c: c.execute("SELECT 1")
    return JsonResponse({"status":"ok","service":"ZeroBite API"})
urlpatterns=[path("admin/",admin.site.urls),path("health/",health),path("api/auth/",include("users.urls")),path("api/donations/",include("donations.urls"))]
