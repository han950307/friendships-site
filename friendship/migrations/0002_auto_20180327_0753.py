# Generated by Django 2.0.2 on 2018-03-27 07:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('friendship', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bids', to='friendship.Order'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='orderaction',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to='friendship.Order'),
        ),
        migrations.AlterField(
            model_name='shipperlist',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shipping_addresses', to=settings.AUTH_USER_MODEL),
        ),
    ]