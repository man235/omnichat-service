# Generated by Django 3.2.14 on 2022-10-12 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('live_chat', '0006_alter_livechat_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='livechat',
            name='avatar_url',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]