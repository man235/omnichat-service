# Generated by Django 3.2.14 on 2022-09-13 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_connect', '0004_auto_20220912_1018'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='room_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]