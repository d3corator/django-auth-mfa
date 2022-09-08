from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

app_name = "auth_mfa"

urlpatterns = [
    path('mfa/token/', MultiFactorTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('mfa/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('mfa/toggle/multi_factor/auth/', ToggleMultiFactorView.as_view(), name='toggle_multi_factor'),
    path('mfa/verify/otp/', VerifyOTPView.as_view(), name='verify_otp'),
]
