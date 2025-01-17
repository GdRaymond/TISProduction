# Generated by Django 2.0.2 on 2018-04-30 01:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20180427_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='cartons',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='volumes',
            field=models.DecimalField(blank=True, decimal_places=3, default=0, max_digits=5, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='weights',
            field=models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=7, null=True),
        ),
        migrations.AlterField(
            model_name='samplecheck',
            name='check_date',
            field=models.DateField(default=datetime.date(2018, 4, 30)),
        ),
    ]
