# Generated by Django 3.2.14 on 2022-09-15 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_connect', '0005_room_room_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='name',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
