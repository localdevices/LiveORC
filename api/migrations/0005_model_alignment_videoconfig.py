from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copy_camera_config_to_video_config(apps, schema_editor):
    CameraConfig = apps.get_model("api", "CameraConfig")
    VideoConfig = apps.get_model("api", "VideoConfig")
    Video = apps.get_model("api", "Video")

    for camera_config in CameraConfig.objects.all().iterator():
        VideoConfig.objects.update_or_create(
            id=camera_config.id,
            defaults={
                "name": camera_config.name,
                "camera_config_id": camera_config.id,
                "site_id": camera_config.site_id,
                "recipe_id": getattr(camera_config, "recipe_id", None),
                "cross_section_id": getattr(camera_config, "profile_id", None),
                "cross_section_wl_id": None,
                "rvec": [],
                "tvec": [],
                "creator_id": camera_config.creator_id,
            },
        )

    for video in Video.objects.exclude(camera_config_id=None).iterator():
        video.video_config_id = video.camera_config_id
        video.save(update_fields=["video_config"])


def copy_video_config_to_camera_config(apps, schema_editor):
    CameraConfig = apps.get_model("api", "CameraConfig")
    VideoConfig = apps.get_model("api", "VideoConfig")
    Video = apps.get_model("api", "Video")

    for video_config in VideoConfig.objects.all().iterator():
        camera_config = CameraConfig.objects.filter(id=video_config.camera_config_id).first()
        if not camera_config:
            continue
        if hasattr(camera_config, "recipe_id"):
            camera_config.recipe_id = video_config.recipe_id
        if hasattr(camera_config, "profile_id"):
            camera_config.profile_id = video_config.cross_section_id
        camera_config.save()

    for video in Video.objects.exclude(video_config_id=None).iterator():
        vc = VideoConfig.objects.filter(id=video.video_config_id).first()
        if vc is None:
            continue
        video.camera_config_id = vc.camera_config_id
        video.save(update_fields=["camera_config"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0004_timeseries_q_raw_timeseries_v_av_timeseries_v_bulk"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Profile",
            new_name="CrossSection",
        ),
        migrations.AlterModelTable(
            name="crosssection",
            table="api_profile",
        ),
        migrations.CreateModel(
            name="VideoConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Recognizable unique name for the video configuration", max_length=100)),
                ("rvec", models.JSONField(blank=True, default=list)),
                ("tvec", models.JSONField(blank=True, default=list)),
                (
                    "site",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="api.site"),
                ),
                (
                    "camera_config",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="camera_configs", to="api.cameraconfig"),
                ),
                (
                    "cross_section",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="video_configs_discharge", to="api.crosssection"),
                ),
                (
                    "cross_section_wl",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="video_configs_water_level", to="api.crosssection"),
                ),
                (
                    "creator",
                    models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
                ),
                (
                    "recipe",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="api.recipe"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="timeseries",
            name="misc",
            field=models.JSONField(blank=True, help_text="Miscellaneous data from time series processes", null=True),
        ),
        migrations.AddField(
            model_name="video",
            name="video_config",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="api.videoconfig"),
        ),
        migrations.RunPython(copy_camera_config_to_video_config, copy_video_config_to_camera_config),
        migrations.RemoveField(
            model_name="cameraconfig",
            name="profile",
        ),
        migrations.RemoveField(
            model_name="cameraconfig",
            name="recipe",
        ),
        migrations.RenameField(
            model_name="cameraconfig",
            old_name="camera_config",
            new_name="data",
        ),
        migrations.RenameField(
            model_name="crosssection",
            old_name="data",
            new_name="features",
        ),
        migrations.RemoveField(
            model_name="video",
            name="camera_config",
        ),
        migrations.AddIndex(
            model_name="video",
            index=models.Index(fields=["video_config", "timestamp"], name="api_video_videoco_4c47d3_idx"),
        ),
    ]
