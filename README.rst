
                =================
                 Django Auth MFA
                =================

Django-auth-mfa is a django app developed on the base of following modules to implement Multi Factor Authentication
in Django Rest Framework using JSON Web Token terminology.

*   Django Rest FrameWork
*   Simple JWT
*   PyJWT
*   PyOTP


                =============
                 Quick Start
                =============

1.  Add "auth_mfa" to your INSTALLED_APPS setting like this:

        INSTALLED_APPS = [
                ...
                'auth_mfa',
                ...
        ]

2.  Include the auth_mfa URLconf in your project urls.py like this:

        path('', include('auth_mfa.urls')),

3.  Now add following code in your project settings.py file

        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': (
                'auth_mfa.authentication.MultiFactorJWTAuthentication',
            )
        }

4.  Run ``python manage.py migrate`` to create the auth_mfa models.

5.  You are all set to go now.....!


Following are the urls you can use to work around this module,


1.  'mfa/token/'
2.  'mfa/token/refresh/'
3.  'mfa/toggle/multi_factor/auth/'
4.  'mfa/verify/otp/'



1 =>    This is a post API used to get access & refresh token. POST username & password to get tokens in Response.

        {
            "username": "bilal",
            "password": "abcd@1234"
        }


2 =>    Post "refresh_token" to this API and get a new "access_token".

        {"refresh": "refresh_token here"}


3 =>    This API is used to toggle multi_factor authentication for a user.

        {
            "password": "1234",                             ( required )
            "authy": true,                                  ( optional )
            "sms": true,                                    ( optional )
            "phone": "03023783386"                          ( optional )
        }

        If "authy" is true, then we will get a url in Response, which will be converted to a QR code and can be scan by Google Authenticator OR Authy app.
        Make "sms" true, if you want to get OTP on your mobile device as sms everytime you login.

        Phone number is compulsory to send if sms is true.

        If you don't want to get mobile sms, make "sms" equals "false".

        If both "authy" & "sms" are false, a url will be returned to make QR and scan.

4 =>    This is used for following two purposes,

        ["GET"]     When make a GET request, it will send a new OTP to your mobile device.
        ["POST"]    when make a POST request, we have to post OTP. It returns new access & refresh tokens.


The tokens have following data in payload, if multi_factor is disabled for a user.

    {
        "token_type": "access",
        "exp": 1662546450,
        "iat": 1662542850,
        "jti": "90ef3dbe34414db3b7fd2581a6602942",
        "user_id": 1,
        "multi_factor": false
    }

    if multi_factor is enabled for a user,

    {
        "token_type": "access",
        "exp": 1662546450,
        "iat": 1662542850,
        "jti": "90ef3dbe34414db3b7fd2581a6602942",
        "user_id": 1,
        "multi_factor": true,
        "otp_verified": false,
        "sms": false
    }

user_id:        it is the id of user logged in.
multi_factor:   true, when multi factor is enabled for the user.
otp_verified:   true, if otp is verified otherwise false.
sms:            true, if user enabled sms OTPs.


To add custom payload in token:


1.  In serializers.py file,

    from auth_mfa.serializers import MultiFactorTokenObtainPairSerializer

    class MyTokenObtainPairSerializer(MultiFactorTokenObtainPairSerializer):
        token = super().get_token(user)

        # add custom data

        token["my_data"] = value
        token["my_data"] = value

        return token

    
2.  In Views.py file,

    from rest_framework_simplejwt.views import TokenObtainPairView
    from .serializers import MyTokenObtainPairSerializer


    class MultiFactorTokenObtainPairView(TokenObtainPairView):
        serializer_class = MyTokenObtainPairSerializer


3.  Now in your project's urls.py file add following path before URLs of "auth_mfa" urls.

        urlpatterns = [
            ...
            path('mfa/token/', MultiFactorTokenObtainPairView.as_view()),
            path('', include('auth_mfa.urls')),
            ...
        ]

    Don't forget to import your "MultiFactorTokenObtainPairView".


You can also change following two settings in your project's setting.

    DJANGO_MFA = {
        "ISSUER_NAME": "Company Name",
        "VALID_WINDOW": 2
    }



ISSUER_NAME:    It is used in QR making.
VALID_WINDOW:   It is used to increase the time of an OTP. (default is 1)

                1 =>    life of two tokens      (1:00 min)
                2 =>    life of three tokens    (1:30 min)
