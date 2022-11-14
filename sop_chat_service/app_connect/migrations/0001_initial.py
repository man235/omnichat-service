# Generated by Django 3.2.14 on 2022-11-14 08:32

import django.contrib.postgres.fields
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
                ('access_token_page', models.CharField(blank=True, max_length=12288, null=True)),
                ('refresh_token_page', models.CharField(blank=True, max_length=12288, null=True)),
                ('avatar_url', models.CharField(blank=True, max_length=255, null=True)),
                ('is_active', models.BooleanField(default=False, null=True)),
                ('app_secret_key', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_subscribe', models.DateTimeField(blank=True, null=True)),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('type', models.CharField(choices=[('facebook', 'Facebook'), ('zalo', 'Zalo'), ('livechat', 'Live Chat')], default='facebook', max_length=30)),
                ('fanpage_user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('is_deleted', models.BooleanField(null=True)),
                ('group_user', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200, null=True), blank=True, null=True, size=None)),
                ('setting_chat', models.CharField(default='only_me', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=255, null=True)),
                ('fb_message_id', models.CharField(blank=True, max_length=255, null=True)),
                ('sender_id', models.CharField(blank=True, max_length=255, null=True)),
                ('recipient_id', models.CharField(blank=True, max_length=255, null=True)),
                ('reaction', models.CharField(choices=[('like', 'Like'), ('haha', 'Haha'), ('love', 'Love'), ('wow', 'Wow'), ('sad', 'Sad'), ('angry', 'Angry'), ('yay', 'Yay')], max_length=30, null=True)),
                ('is_forward', models.BooleanField(default=False, null=True)),
                ('reply_id', models.IntegerField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('sender_name', models.CharField(blank=True, max_length=255, null=True)),
                ('is_seen', models.DateTimeField(blank=True, null=True)),
                ('is_sender', models.BooleanField(default=False, null=True)),
                ('remove_for_you', models.BooleanField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('timestamp', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('unit', models.CharField(choices=[('day', 'Day'), ('hour', 'Hour'), ('minute', 'Minute'), ('second', 'Second')], default='hour', max_length=30)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('time_reminder', models.IntegerField(blank=True, null=True)),
                ('repeat_time', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('avatar', models.URLField(blank=True, max_length=10000, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=13, null=True)),
                ('gender', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceSurvey',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('value', models.CharField(blank=True, max_length=1000, null=True)),
                ('mid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_message_id', to='app_connect.message')),
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
                ('type', models.CharField(choices=[('facebook', 'Facebook'), ('zalo', 'Zalo'), ('livechat', 'Live Chat')], default='facebook', max_length=30)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('conversation_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('room_id', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('all', 'All'), ('processing', 'Processing'), ('completed', 'Completed'), ('expired', 'Expired')], default='processing', max_length=30)),
                ('admin_room_id', models.CharField(blank=True, max_length=255, null=True)),
                ('block_admin', models.BooleanField(null=True)),
                ('page_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fanPage_room', to='app_connect.fanpage')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='room_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='room_message', to='app_connect.room'),
        ),
        migrations.CreateModel(
            name='LogMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_type', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.CharField(blank=True, max_length=500, null=True)),
                ('room_id', models.CharField(blank=True, max_length=255, null=True)),
                ('from_user', models.CharField(blank=True, max_length=255, null=True)),
                ('to_user', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('mid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='log_message_id', to='app_connect.message')),
            ],
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_id', models.CharField(blank=True, max_length=255, null=True)),
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
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('size', models.IntegerField(blank=True, null=True)),
                ('mid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_id', to='app_connect.message')),
            ],
        ),
        migrations.CreateModel(
            name='AssignReminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=255, null=True)),
                ('unit', models.CharField(blank=True, max_length=30, null=True)),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('time_reminder', models.IntegerField(blank=True, null=True)),
                ('repeat_time', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_active_reminder', models.BooleanField(default=False)),
                ('reminder_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assign_reminder', to='app_connect.reminder')),
                ('room_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='room_reminder', to='app_connect.room')),
            ],
        ),
    ]
