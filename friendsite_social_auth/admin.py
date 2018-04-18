from django.contrib import admin
from friendsite_social_auth.models import (
	FacebookUser,
	LineUser,
)

# Register your models here.
admin.site.register(FacebookUser)
admin.site.register(LineUser)
