# Generated by Django 3.2.14 on 2022-08-23 16:53

from django.db import migrations, models
import django.db.models.deletion
import sop_chat_service.utils.storages


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FanPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_id', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('access_token_page', models.CharField(blank=True, max_length=255, null=True)),
                ('avatar_url', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False, null=True)),
                ('app_secret_key', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_subscribe', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=255, null=True)),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('note', models.CharField(blank=True, max_length=255, null=True)),
                ('approved_date', models.DateTimeField(blank=True, null=True)),
                ('type', models.CharField(choices=[('facebook', 'Facebook'), ('zalo', 'Zalo')], default='facebook', max_length=30)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('conversation_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('page_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fanPage_room', to='app_connect.fanpage')),
            ],
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(choices=[('day', 'Day'), ('hour', 'Hour'), ('minute', 'Minute'), ('second', 'Second')], default='hour', max_length=30)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('time_reminder', models.IntegerField(blank=True, null=True)),
                ('repeat_time', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='room_reminder', to='app_connect.room')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_message_id', models.CharField(blank=True, max_length=255, null=True)),
                ('sender_id', models.CharField(blank=True, max_length=255, null=True)),
                ('recipient_id', models.CharField(blank=True, max_length=255, null=True)),
                ('reaction', models.CharField(choices=[('like', 'Like'), ('haha', 'Haha'), ('love', 'Love'), ('wow', 'Wow'), ('sad', 'Sad'), ('angry', 'Angry'), ('yay', 'Yay')], max_length=30, null=True)),
                ('is_forward', models.BooleanField(default=False, null=True)),
                ('reply_id', models.IntegerField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('sender_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_seen', models.DateTimeField(blank=True, null=True)),
                ('remove_for_you', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='room_message', to='app_connect.room')),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('color', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='room_label', to='app_connect.room')),
            ],
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attachment_id', models.CharField(blank=True, max_length=255, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to=sop_chat_service.utils.storages.upload_image_to)),
                ('type', models.CharField(blank=True, max_length=255, null=True)),
                ('url', models.CharField(blank=True, max_length=500, null=True)),
                ('mid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_id', to='app_connect.message')),
            ],
        ),
    ]
