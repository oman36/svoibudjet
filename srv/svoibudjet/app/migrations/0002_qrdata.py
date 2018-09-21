# Generated by Django 2.0.5 on 2018-09-21 14:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='QRData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('qr_string', models.CharField(max_length=255)),
                ('is_valid', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('check_model', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.Check')),
            ],
        ),
    ]
