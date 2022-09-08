from setuptools import setup

setup(
    name='django-auth-mfa',
    version='1.0.0',
    zip_safe = False,
    install_requires=[
        'django',
        'djangorestframework',
        'djangorestframework-simplejwt',
        'PyJWT',
        'pyotp',
    ],
)