from django.urls import path
from .views import RegisterView, LoginView, RefreshView, MeView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("token/", LoginView.as_view()),
    path("token/refresh/", RefreshView.as_view()),
    path("me/", MeView.as_view()),
]
