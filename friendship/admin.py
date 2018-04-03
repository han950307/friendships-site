from django.contrib import admin
from .models import (
	ShipperInfo,
	ShippingAddress,
	Order,
	Bid,
	Image,
	Message,
	OrderAction
)


# Register your models here.
admin.site.register(ShippingAddress)
admin.site.register(ShipperInfo)
admin.site.register(Order)
admin.site.register(Bid)
admin.site.register(Image)
admin.site.register(Message)
admin.site.register(OrderAction)
