# Generated by Django 3.2.14 on 2022-11-09 09:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_connect', '0022_auto_20221109_0748'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignreminder',
            name='is_active_reminder',
            field=models.BooleanField(default=False),
        ),
    ]