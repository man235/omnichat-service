# Generated by Django 3.2.14 on 2022-08-29 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_connect', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_sender',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
