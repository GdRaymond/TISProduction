# Generated by Django 2.0.2 on 2018-03-28 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_auto_20180315_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='volume_per_carton',
            field=models.DecimalField(decimal_places=3, max_digits=4),
        ),
    ]