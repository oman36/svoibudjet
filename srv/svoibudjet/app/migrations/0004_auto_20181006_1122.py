# Generated by Django 2.0.5 on 2018-10-06 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20180923_1310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='qrdata',
            name='qr_string',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]