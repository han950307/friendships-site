from django.shortcuts import (render, redirect)
from marketing_manager.models import FAQ
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import (
    login_required,
)
from marketing_manager.forms import FAQEditForm

import re
# Create your views here.


def faq(request):
    # Singletone faq
    if not FAQ.objects.all():
        FAQ.objects.create(inner_HTML="<h4>Question title</h4>\n<p>Question answer</p>")

    faq_html = re.sub(r"\n", "", FAQ.objects.all()[0].inner_HTML)

    # if multiple orders or no order found with that id.
    return render (
        request, 'marketing_manager/faq.html', {'content': faq_html}
    )


@staff_member_required
@login_required
def edit_faq(request):
    if request.method == 'POST':
        form = FAQEditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data["inner_HTML"]
            faq = FAQ.objects.all()[0]
            faq.inner_HTML = data
            faq.save()
            return redirect('marketing_manager:faq')
    else:
        form = FAQEditForm(instance=FAQ.objects.all()[0])

    return render(request, 'marketing_manager/edit_faq.html', {'form': form})
