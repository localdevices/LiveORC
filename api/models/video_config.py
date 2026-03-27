from django.db import models

from api.models.site import Site

from .base import BaseModel
from .camera_config import CameraConfig
from .recipe import Recipe
from .cross_section import CrossSection


class VideoConfig(BaseModel):
    """Configuration that combines processing dependencies for videos."""

    name = models.CharField(max_length=100, help_text="Recognizable unique name for the video configuration")
    camera_config = models.ForeignKey(CameraConfig, on_delete=models.CASCADE, related_name="camera_configs")
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    cross_section = models.ForeignKey(
        CrossSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_configs_discharge",
    )
    cross_section_wl = models.ForeignKey(
        CrossSection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="video_configs_water_level",
    )
    rvec = models.JSONField(default=list, blank=True)
    tvec = models.JSONField(default=list, blank=True)


    def __str__(self):
        return f"{self.name} at {self.camera_config.site.name}"

    @property
    def institute(self):
        return self.site.institute
