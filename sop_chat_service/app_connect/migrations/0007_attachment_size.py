# Generated by Django 3.2.14 on 2022-09-16 07:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_connect', '0006_attachment_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]