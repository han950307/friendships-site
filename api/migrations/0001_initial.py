# Generated by Django 2.0.3 on 2018-03-30 03:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='LineUser',
            fields=[
                ('line_user_id', models.CharField(max_length=200, unique=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='line_user_id', serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
