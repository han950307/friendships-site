from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class LineUser(models.Model):
    line_user_id = models.CharField(max_length=200, unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="line_user_id",
    )
