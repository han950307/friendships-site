from django.db import models

# Create your models here.
class FAQ(models.Model):
    """
    Contains a list of shippers.
    """
    inner_HTML = models.TextField(null=True, blank=True)
    inner_HTML_thai = models.TextField(null=True, blank=True)
