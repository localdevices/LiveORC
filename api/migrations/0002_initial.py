# Generated by Django 4.2.3 on 2024-05-16 13:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='video',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.project'),
        ),
        migrations.AddField(
            model_name='video',
            name='time_series',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.timeseries'),
        ),
        migrations.AddField(
            model_name='timeseries',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='timeseries',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.site'),
        ),
        migrations.AddField(
            model_name='taskform',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='taskform',
            name='device',
            field=models.ForeignKey(help_text='Device for which task form is meant', on_delete=django.db.models.deletion.CASCADE, to='api.device'),
        ),
        migrations.AddField(
            model_name='taskform',
            name='institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute'),
        ),
        migrations.AddField(
            model_name='task',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='task',
            name='video',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.video'),
        ),
        migrations.AddField(
            model_name='site',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='site',
            name='institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute'),
        ),
        migrations.AddField(
            model_name='server',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='server',
            name='institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute'),
        ),
        migrations.AddField(
            model_name='project',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.institute'),
        ),
        migrations.AddField(
            model_name='profile',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='profile',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.site'),
        ),
        migrations.AddField(
            model_name='device',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cameraconfig',
            name='creator',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cameraconfig',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.profile'),
        ),
        migrations.AddField(
            model_name='cameraconfig',
            name='recipe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.recipe'),
        ),
        migrations.AddField(
            model_name='cameraconfig',
            name='server',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.server'),
        ),
        migrations.AddField(
            model_name='cameraconfig',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.site'),
        ),
        migrations.AddIndex(
            model_name='video',
            index=models.Index(fields=['camera_config', 'timestamp'], name='api_video_camera__7fea15_idx'),
        ),
        migrations.AddIndex(
            model_name='timeseries',
            index=models.Index(fields=['site', 'timestamp'], name='api_timeser_site_id_c07d34_idx'),
        ),
    ]