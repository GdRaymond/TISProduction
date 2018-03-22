# Generated by Django 2.0.2 on 2018-03-14 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shipments', '0002_auto_20180314_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='shipment',
            name='code',
            field=models.TextField(default='dd', max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='shipment',
            name='container',
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
    ]
