from django.contrib import admin
from .models import (
	Bid,
	Flight,
	Message,
	Money,
	Order,
	OrderAction,
	PaymentAction,
	ShipperInfo,
	ShippingAddress,
	TrackingNumber,
)


# Register your models here.
admin.site.register(Bid)
admin.site.register(Flight)
admin.site.register(Message)
admin.site.register(Money)
admin.site.register(Order)
admin.site.register(OrderAction)
admin.site.register(PaymentAction)
admin.site.register(ShipperInfo)
admin.site.register(ShippingAddress)
admin.site.register(TrackingNumber)
