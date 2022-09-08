import jwt

from .models import MultiFactor

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.exceptions import InvalidToken


class MultiFactorJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        try:
            token = jwt.decode(raw_token, api_settings.SIGNING_KEY, algorithms=[api_settings.ALGORITHM])
        except:
            token = {'multi_factor': False, 'otp_verified': False}
        if token['multi_factor'] and token['otp_verified'] == False:
            if not MultiFactor.check_url(request):
                raise InvalidToken(
                    {
                        "detail": ("This token can only be used for OTP Verification."),
                    }
                )
        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
