import decimal

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LOCAL = True

# Service fee is item price * this number
SERVICE_FEE_RATE = decimal.Decimal(0.165)

# This is the value when time left fraction is 1, and is multiplied by wages.
BID_TRICKLE_RATIO = decimal.Decimal(0.4)

# When the cron runs, do a random bid with this percent likelihood.
BID_TRICKLE_ACCEPT_PROBABILITY = decimal.Decimal(0.3)

# This is the manual bank transfer discount.
MANUAL_BANK_TRANSFER_DISCOUNT = decimal.Decimal(0.04)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7@r-lqamj-2=za3b1lp+#d#fr)u4705e!)2azohsg=q1#@+7#_'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '35/second',
        'user': '300/second'
    }
}

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if DEBUG and LOCAL:
    db_name = 'friendship'
    db_pass = 'friend'
    db_host = '127.0.0.1'
elif DEBUG and not LOCAL:
    db_name = 'friendships'
    db_pass = 'togetheragain'
    db_host = '35.174.169.71'
elif not DEBUG:
    db_name = 'friendships'
    db_pass = 'wehavepowerfulfriends'
    db_host = 'prod-db.ceynexuoclm4.us-east-1.rds.amazonaws.com'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': 'root',
        'PASSWORD': db_pass,
        'HOST': db_host,
        'PORT': '5432',
    }
}

# Email stuff
EMAIL_HOST = '54.225.141.170'
EMAIL_HOST_USER = 'AKIAIL2IYGVWPDWPVHTQ'
EMAIL_HOST_PASSWORD = 'Amf8+tkc9IGwl1DKpOUT5AkgAz3dQ9ZQCKYDu86aPRDX'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'no-reply@friendships.us'

# Social Auth APIS
if DEBUG:
    FACEBOOK_REDIRECT_URI = "https://dev.friendships.us/social_auth/facebook_callback/"
else:
    FACEBOOK_REDIRECT_URI = "https://www.friendships.us/social_auth/facebook_callback/"

FACEBOOK_API_URL = "facebook.com/v2.12"
FACEBOOK_CLIENT_ID = "148610779299581"
FACEBOOK_CLIENT_SECRET = "af36969a93543ad21332bbe130f0ee0b"
FACEBOOK_ACCESS_TOKEN = "148610779299581|af36969a93543ad21332bbe130f0ee0b"
FACEBOOK_CLIENT_TOKEN = "25f78b1cd5f5d29c54637353717d7e42"

AWS_ACCESS_KEY_ID = "AKIAJGNIR26GDQKGCSPA"
AWS_SECRET_ACCESS_KEY = "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"
AWS_STORAGE_BUCKET_NAME = 'media.friendships.us'
AWS_S3_CUSTOM_DOMAIN = '{}'.format(AWS_STORAGE_BUCKET_NAME)
AWS_S3_SECURE_URLS = False
DEFAULT_FILE_STORAGE = 'friendship.storage_backends.MediaStorage'

if DEBUG:
    if LOCAL:
        LINE_REDIRECT_URI = "http://127.0.0.1:8000/social_auth/line_callback/"
    else:
        LINE_REDIRECT_URI = "https://dev.friendships.us/social_auth/line_callback/"
else:
    LINE_REDIRECT_URI = "https://www.friendships.us/social_auth/line_callback/"
LINE_AUTH_URL = "https://access.line.me/dialog/oauth/weblogin"
LINE_CLIENT_ID = "1569916870"
LINE_CLIENT_SECRET = "d5ac52402b435291373b5654a7df7a7c"

LINE_SECRET_CODE = "017682"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
if LOCAL:
    STATIC_ROOT = 'friendship/static/friendship/'
    MEDIA_ROOT = 'friendship/media/friendship/'
else:
    STATIC_ROOT = '/home/ubuntu/static'
    MEDIA_ROOT = AWS_S3_CUSTOM_DOMAIN

STATIC_URL = '/static/'

if LOCAL:
    MEDIA_URL = '/media/'
else:
    MEDIA_URL = AWS_S3_CUSTOM_DOMAIN + "/"

OMISE_PUBLIC = 'pkey_test_5bhaufrx5qsyotldxvl'
OMISE_SECRET = 'skey_test_5bhaufrxoxs9f91z57v'


if DEBUG:
    BRAINTREE_ACCOUNT = 'friendships-facilitator@friendships.us'
    BRAINTREE_ACCESS_TOKEN = 'access_token$sandbox$5v32t72jn7yqtygt$048d19861d130456b40404a1eaef92ff'
    PAYPAL_ACCOUNT = 'friendships-facilitator@friendships.us'
    PAYPAL_ID = 'AQ55vA8iM7cvNz656zlBmNCCv5QBu41Ps0H7itZ8lVSiFmBPX2ebaVrW9MUIgDz97jV92_j_cEFQm1qn'
    PAYPAL_SECRET = 'EEp5bviuT9DggPhBPsFYBv-9tYn6qbuG0V2et7tylwd4pRqsnTYh6hh5u7bgV58wkjZCEn9C-Wbgk4aC'
else:
    BRAINTREE_ACCOUNT = 'friendships@friendships.us'
    BRAINTREE_ACCESS_TOKEN = 'access_token$production$wcwthspyzhzx6v6k$cc2fa43062a7e35d7103402f27453664'
    PAYPAL_ACCOUNT = 'friendships@friendships.us'
    PAYPAL_ID = 'AaALdiffOahjW9uimEeqXR7b9O4wIBSk0dj9m08EGzu7pZ5Ok6-GZ0oPW7TFTUHmEtr2xjtxyuTosmI5'
    PAYPAL_SECRET = 'EEpUDRzAj7ZPldYoVhJGBo6g7bluV14OrQPN4NvdJwnm9rtxjHN_6k2u3hKncfh_WZsnBvPLoyAsxXA7'
