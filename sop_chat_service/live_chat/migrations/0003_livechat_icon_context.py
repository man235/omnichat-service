# Generated by Django 3.2.14 on 2022-09-19 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_chat', '0002_userlivechat'),
    ]

    operations = [
        migrations.AddField(
            model_name='livechat',
            name='icon_context',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
