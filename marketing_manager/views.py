from django.shortcuts import render
from marketing_manager.models import FAQ

import re
# Create your views here.

def faq(request):
    # Singletone faq
    if not FAQ.objects.all():
        FAQ.objects.create(inner_HTML="<h2>Question title</h2>\n<<p>Question answer</p>")

    faq_html = re.sub(r"\n", "", FAQ.objects.all()[0].inner_HTML)

    # if multiple orders or no order found with that id.
    return render (
        request, 'marketing_manager/faq.html', {'html': faq_html}
    )
