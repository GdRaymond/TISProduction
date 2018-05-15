# Generated by Django 2.0.2 on 2018-04-26 23:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20180420_1134'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cartons',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='order_date',
            field=models.DateField(default=datetime.date(2018, 4, 27)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='tape_no',
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='volumes',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='order',
            name='weights',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=7),
        ),
        migrations.AlterField(
            model_name='samplecheck',
            name='check_date',
            field=models.DateField(default=datetime.date(2018, 4, 27)),
        ),
    ]