from django.shortcuts import (
	render,
	redirect,
)

from backend.views import (
	create_order,
)

from friendship.models import (
	Order,
	ShippingAddress,
	OrderAction,
)

from friendship.forms import (
	UploadPictureForm,
	OrderForm,
)
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.contrib import messages
from friendsite import settings
import datetime
import requests
import pytz
import omise
import base64


@login_required
def upload_picture_view(request, order_id):
	orders = Order.objects.filter(pk=order_id)

	# if multiple orders or no order found with that id.
	if len(orders) != 1:
		messages.error(request, 'Order not found')
		return redirect('friendship:receiver_landing')
	else:
		order = orders[0]
		return render(
			request,
			'friendship/upload_picture.html',
			{'order': order}
		)


@login_required
def upload_picture_process(request, order_id):
	if request.method == "POST":
		form = UploadPictureForm(request.POST, request.FILES)
		order = Order.objects.get(pk=order_id)

		if form.is_valid():
			imagef = form.cleaned_data["picture"]
			# encoded_string = base64.b64encode(imagef.read())
			# image = Image.objects.create(
			# 	user=request.user,
			# 	order=order,
			# 	image=encoded_string,
			# 	mimetype="0",
			# 	image_type=0,
			# )
			action = OrderAction.objects.create(
				order=order,
				action=OrderAction.Action.BANKNOTE_UPLOADED
			)
			order.latest_action = action
			order.save()
			return redirect('friendship:order_details', pk=order_id)
		else:
			messages.error(request, 'Bad image')
			return redirect('friendship:upload_picture_view', order_id=order_id)
	else:
		messages.debug(request, 'Must be a post request')
		return redirect('friendship:order_details', pk=order_id)


@login_required
def make_payment(request, order_id):
	return render(request, 'friendship/make_payment.html', {'order_id': order_id})


@login_required
def process_payment(request, order_id):
	order = Order.objects.get(pk=order_id)
	total_amount = order.final_bid.get_total()
	currency = order.final_bid.currency
	description = "Order-{}".format(order_id)
	if settings.DEBUG and settings.LOCAL:
		return_uri = "http://127.0.0.1:8000/"
	elif settings.DEBUG:
		return_uri = "https://dev.friendships.us/"
	else:
		return_uri = "https://www.friendships.us/"
	if order.receiver != request.user:
		print(order.receiver, request.user)
		return redirect('friendship:receiver_landing')
	omise_token = request.POST['omise_token']

	print(omise_token)

	omise.api_secret = settings.OMISE_SECRET
	omise.api_public = settings.OMISE_PUBLIC

	charge = omise.Charge.create(
		amount=int(total_amount * 100),
		currency="usd",
		card=omise_token,
		description=description,
	)

	if charge.authorized == True:
		action = OrderAction.objects.create(
			order=order,
			action=OrderAction.Action.PAYMENT_RECEIVED,
		)
		order.latest_action = action
		order.save()
		messages.success(request, "Payment processed.")
		redirect('friendship:receiver_landing')

	# for now, just get the min
	return render(request, 'friendship/index.html', {})

@login_required
def receiver_landing(request):
	return render(request, 'friendship/receiver_landing.html', {
		'data': [request, ],
	})


@login_required
def place_order(request):
	"""
	This is a page for a form for making an order.
	"""
	OrderFormSet = formset_factory(OrderForm)
	if request.method != 'POST':
		# TODO Should display all the forms.
		formset = OrderFormSet()
		primary_address = ShippingAddress.objects.filter(
			user=request.user
		).filter(
			primary=True
		)
		if primary_address:
			address = primary_address[0]
		else:
			address = None
		return render(
			request,
			'friendship/place_order.html',
			{
				'address': address, 'formset': formset,
			},
			)
	else:
		# TODO change hardcoded things.
		req = request.POST
		num = req['form-TOTAL_FORMS']
		orders = {}
		for i in range(int(num)):
			data_dict = {
				'url': req['form-' + str(i) + '-url'],
				'merchandise_type': req['form-' + str(i) + '-merchandise_type'],
				'quantity': int(req['form-' + str(i) + '-quantity']),
				'description': req['form-' + str(i) + '-description'],
				'receiver': request.user,
				'receiver_address': ShippingAddress.objects.all()[0],
				'estimated_weight': 1,
				'bid_end_datetime': datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
								 + datetime.timedelta(hours=int(req['form-' + str(i) + '-quantity']))
			}
			order = create_order(request.user, **data_dict)
			orders[i] = order

		return render(request, 'friendship/place_order_landing.html', {'orders': orders})
