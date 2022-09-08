from django.conf import settings

django_mfa = getattr(settings, "DJANGO_MFA", dict())

Defaults = {
    "ISSUER_NAME": django_mfa.get('ISSUER_NAME', 'Synares'),
    "VALID_WINDOW": django_mfa.get('VALID_WINDOW', 1)
}


class DjangoMFASettings:
    pass


mfa_settings = DjangoMFASettings()

for key, value in Defaults.items():
    setattr(mfa_settings, key, value)
