from django.urls import path
from .views import LoginView
from rest_framework_simplejwt.views import TokenVerifyView


urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('verify/', TokenVerifyView.as_view(), name="verify")
]