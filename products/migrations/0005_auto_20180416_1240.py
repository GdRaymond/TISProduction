# Generated by Django 2.0.2 on 2018-04-16 02:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20180328_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fabric',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fabric', models.TextField(max_length=200)),
            ],
            options={
                'verbose_name': 'Fabric',
                'verbose_name_plural': 'Fabrics',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='client',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='fabric',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='products.Fabric'),
            preserve_default=False,
        ),
    ]
