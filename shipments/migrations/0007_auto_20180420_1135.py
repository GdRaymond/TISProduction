# Generated by Django 2.0.2 on 2018-04-20 01:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0006_auto_20180403_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shipment',
            name='etd',
            field=models.DateField(default=datetime.date(2018, 4, 20)),
        ),
    ]
