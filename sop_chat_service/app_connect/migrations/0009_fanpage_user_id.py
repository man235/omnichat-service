# Generated by Django 3.2.14 on 2022-09-22 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_connect', '0008_auto_20220920_0758'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanpage',
            name='user_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
