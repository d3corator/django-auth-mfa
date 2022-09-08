import pyotp

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from .settings import mfa_settings


class MultiFactor(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    key = models.CharField(max_length=50, default=None, null=True, blank=True)
    sms = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, default=None, null=True, blank=True)

    @classmethod
    def exists(cls, user) -> bool:
        obj = MultiFactor.objects.filter(user=user).first()
        if obj:
            if obj.key:
                return True
        return False

    @classmethod
    def verify(cls, user, otp) -> bool:
        try:
            obj = MultiFactor.objects.filter(user=user).first()
            totp = pyotp.TOTP(obj.key)
            if totp.verify(otp, valid_window=mfa_settings.VALID_WINDOW):
                return True
            return False
        except:
            return False

    @classmethod
    def check_url(cls, request):
        if request.get_full_path() == reverse("django_mfa:verify_otp"):
            return True
        return False

    @classmethod
    def send_otp_sms(cls, user):
        obj = MultiFactor.objects.filter(user=user).first()
        if obj.sms:
            totp = pyotp.TOTP(obj.key)
            print(f"Send => OTP: {totp.now()} to Mobile: {obj.phone}")
        return

    @classmethod
    def check_sms_enabled(cls, user):
        obj = MultiFactor.objects.filter(user=user).first()
        if obj.sms:
            return True
        return False
