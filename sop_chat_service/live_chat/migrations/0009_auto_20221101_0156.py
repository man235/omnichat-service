# Generated by Django 3.2.14 on 2022-11-01 01:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_chat', '0008_auto_20221026_0657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livechat',
            name='introduce_message',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='livechat',
            name='offline_message',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='livechat',
            name='start_btn',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='livechat',
            name='start_message',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]