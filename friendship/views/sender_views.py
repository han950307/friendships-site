from django.contrib.auth.decorators import login_required
from django.contrib.messages import error
from django.shortcuts import (
    render,
    redirect,
)
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.mixins import LoginRequiredMixin

from formtools.wizard.views import SessionWizardView

from friendship.models import Order, Bid, ShipperInfo, Money
from friendship.views import open_orders
from friendship.forms import (
    SenderRegistrationForm,
    TravelerRegistrationForm,
    ShippingCompanyRegistrationForm
)
from friendsite import settings

import os

@login_required
def make_bid(request, order_id):
    """
    Make bid view. Allows sender to make a bid for the order.
    """
    if not request.session["is_shipper"]:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        order = Order.objects.get(pk=order_id)
        return render(request, 'friendship/make_bid.html', {'order' : order})


def create_money_object(data_dict, key, currency):
    if key in data_dict:
        val = float(data_dict[key])
        return Money.objects.create(value=val, currency=currency)
    else:
        return None


@login_required
def make_bid_process(request, order_id):
    """
    Processes make bid
    """
    if not request.session["is_shipper"]:
        error(request, 'You do not have permissions to access this page.')
        return redirect('friendship:index')
    else:
        data_dict = {x: v for x, v in request.POST.items()}
        currency = Money.Currency.get_currency(data_dict["currency"])

        order = Order.objects.get(pk=order_id)
        bid = Bid.objects.create(
            order=order,
            shipper=request.user,
            wages=create_money_object(data_dict, "wages", currency),
            retail_price=create_money_object(data_dict, "retail_price", currency),
            import_tax=create_money_object(data_dict, "import_tax", currency),
            dest_domestic_shipping=create_money_object(data_dict, "dest_domestic_shipping", currency),
            origin_domestic_shipping=create_money_object(data_dict, "origin_domestic_shipping", currency),
            international_shipping=create_money_object(data_dict, "international_shipping", currency),
            service_fee=create_money_object(data_dict, "service_fee", currency),
            origin_sales_tax=create_money_object(data_dict, "origin_sales_tax", currency),
            other_fees=create_money_object(data_dict, "other_fees", currency),
        )

        # Just return another view after processing it.
        return open_orders(request, "recent")


class SenderRegistrationWizard(LoginRequiredMixin, SessionWizardView):
    template_name = 'friendship/sender_registration.html'
    form_list = [SenderRegistrationForm]
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'id_images'))

    def done(self, form_list, form_dict, **kwargs):
        user = self.request.user
        shipper_type = int(form_dict['0'].cleaned_data["shipper_type"])
        phone_number = form_dict['1'].cleaned_data["phone_number"]
        shipper_info = ShipperInfo.objects.create(
            user=user,
            shipper_type=shipper_type,
            verified=False,
            phone_number=phone_number,
        )
        if (shipper_type == ShipperInfo.ShipperType.TRAVELER):
            id_image = form_dict['1'].cleaned_data["id_image"]
            shipper_info.id_image = id_image
            shipper_info.name = user.first_name + " " + user.last_name
        elif shipper_type == ShipperInfo.ShipperType.FLIGHT_ATTENDANT:
            pass
        elif shipper_type == ShipperInfo.ShipperType.SHIPPING_COMPANY:
            name = form_dict['1'].cleaned_data["name"]
            shipper_info.name = name
        shipper_info.save()

    def process_step(self, form):
        if "shipper_type" in form.cleaned_data:
            shipper_type = int(form.cleaned_data["shipper_type"])
            if shipper_type == ShipperInfo.ShipperType.TRAVELER:
                self.form_list.update({'1': TravelerRegistrationForm})
            elif shipper_type == ShipperInfo.ShipperType.FLIGHT_ATTENDANT:
                self.form_list.update({'1': ShippingCompanyRegistrationForm})
            elif shipper_type == ShipperInfo.ShipperType.SHIPPING_COMPANY:
                self.form_list.update({'1': ShippingCompanyRegistrationForm})
            else:
                print("NOT FOUND")
        return super(SenderRegistrationWizard, self).process_step(form)


@login_required
def user_open_bids(request):
    """
    This displays all the orders for the receiver.
    """
    qset = Bid.objects.filter(shipper=request.user)
    return render(request, 'friendship/user_open_bids.html', {
        'data': qset,
    })


@login_required
def sender_landing(request):
	return render(request, 'friendship/sender_landing.html', {
		'data': [request, ],
	})
