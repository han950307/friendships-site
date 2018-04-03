from django.contrib.messages import error

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

import datetime
import pytz
import base64


@login_required
def upload_picture_view(request, order_id):
	orders = Order.objects.filter(pk=order_id)

	# if multiple orders or no order found with that id.
	if len(orders) != 1:
		error(request, 'Order not found')
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
			encoded_string = base64.b64encode(imagef.read())
			# image = Image.objects.create(
			# 	user=request.user,
			# 	order=order,
			# 	image=encoded_string,
			# 	mimetype="0",
			# 	image_type=0,
			# )
			OrderAction.objects.create(
				order=order,
				action=OrderAction.Action.BANKNOTE_UPLOADED
			)
			return redirect('friendship:order_details', pk=order_id)
		else:
			error(request, 'Bad image')
			return redirect('friendship:upload_picture_view', order_id=order_id)
	else:
		error(request, 'Must be a post request')
		return redirect('friendship:order_details', pk=order_id)


@login_required
def receiver_landing_view(request):
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
			'friendship/receiver_landing.html',
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
