from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import MultiFactor


class MultiFactorTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user, otp_verified=False):
        token = super().get_token(user)
        if MultiFactor.exists(user):
            token['multi_factor'] = True
            token['otp_verified'] = False
            token['sms'] = MultiFactor.check_sms_enabled(user)
            if not otp_verified:
                MultiFactor.send_otp_sms(user)
        else:
            token['multi_factor'] = False
        if otp_verified:
            token['otp_verified'] = True
        return token
