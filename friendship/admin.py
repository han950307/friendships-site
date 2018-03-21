from django.contrib import admin
from .models import Image
from .models import UserInfo
from .models import Order


# Register your models here.
admin.site.register(Image)
admin.site.register(Order)
admin.site.register(UserInfo)
