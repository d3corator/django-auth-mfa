import pyotp
import jwt

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.settings import api_settings

from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model

from .serializers import MultiFactorTokenObtainPairSerializer
from .models import MultiFactor
from .settings import mfa_settings

User = get_user_model()


class MultiFactorTokenObtainPairView(TokenObtainPairView):
    serializer_class = MultiFactorTokenObtainPairSerializer


class VerifyOTPView(APIView):

    def get(self, request, *args, **kwargs):
        header = request.META.get(api_settings.AUTH_HEADER_NAME)
        parts = header.split()
        token = jwt.decode(parts[1], api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
        user = User.objects.get(pk=token["user_id"])
        MultiFactor.send_otp_sms(user)
        return Response({"detail": "New OTP is sent to your mobile device.", "code": "otp_resent"},
                        status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        if not data.get('otp', None):
            return Response({"detail": "Given OTP is not correct OR get expired.", "code": "wrong_otp"},
                            status=status.HTTP_400_BAD_REQUEST)

        if MultiFactor.verify(request.user, data.get('otp')):
            data = {}
            refresh = MultiFactorTokenObtainPairSerializer.get_token(request.user, otp_verified=True)
            data["refresh"] = str(refresh)
            data["access"] = str(refresh.access_token)

            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, self.user)
            return Response(data)

        return Response({"detail": "Given OTP is not correct OR get expired.", "code": "wrong_otp"},
                        status=status.HTTP_400_BAD_REQUEST)


class ToggleMultiFactorView(APIView):

    # used to enable OR disable multi factor authentication for a user

    def post(self, request, *args, **kwargs):
        data = dict(request.data)
        user = request.user
        user_details = {}
        obj = MultiFactor.objects.filter(user=user).first()

        if user.check_password(data.get('password')):  # password confirmation to toggle multi factor authentication

            if not MultiFactor.exists(user):  # check if multi factor is already enabled
                if data.get('sms', None):
                    user_details['sms'] = True
                    if data.get('phone',
                                None):  # if sms is true, mobile number is necessary to send (if not already saved in table)
                        user_details['phone'] = data.get('phone', None)
                    elif obj:
                        if not obj.phone:  # checking if mobile number is already saved or not
                            return Response(
                                {"detail": "Phone number is required to send OTP to Mobile.", "code": "phone_missing"},
                                status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response(
                            {"detail": "Phone number is required to send OTP to Mobile.", "code": "phone_missing"},
                            status=status.HTTP_400_BAD_REQUEST)
                else:
                    user_details['sms'] = False

            if obj:
                if obj.key:  # if multi factor is enabled, disable it
                    MultiFactor.objects.filter(user=user).update(sms=False, key=None)
                    return Response({"detail": "Multi-Factor authentication disabled successfully.", "code": "success"},
                                    status=status.HTTP_200_OK)
                else:
                    key = pyotp.random_base32()  # updating user data if data already exists
                    user_details["key"] = key
                    MultiFactor.objects.filter(user=user).update(**user_details)
            else:
                key = pyotp.random_base32()  # creating new row in table
                user_details["key"] = key
                MultiFactor.objects.create(user=user, **user_details)

            if data.get('authy', None) or not data.get('sms', None):  # checking either to send QR or just success msg
                return Response({"detail": "Multi-Factor authentication enabled successfully.", "code": "success",
                                 "url": pyotp.totp.TOTP(user_details["key"]).provisioning_uri(name=user.username,
                                                                                              issuer_name=mfa_settings.ISSUER_NAME)},
                                status=status.HTTP_200_OK)
            return Response({"detail": "Multi-Factor authentication enabled successfully.", "code": "success"},
                            status=status.HTTP_200_OK)
        return Response({"detail": "The given password is incorrect.", "code": "wrong_password"},
                        status=status.HTTP_401_UNAUTHORIZED)
