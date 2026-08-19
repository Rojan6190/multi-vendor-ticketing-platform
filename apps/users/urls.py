from django.urls import path
from apps.users.views import RegisterView, MeView, LoginView, RefreshView

urlpatterns = [
    path("register/", RegisterView.as_view(), name = "register"),
    path("me/", MeView.as_view(), name="me"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/refresh/", RefreshView.as_view(), name="login-refresh"),
]