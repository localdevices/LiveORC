import base64
import geopandas as gpd
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pyorc

from django.db import models
from django.utils.html import mark_safe
from shapely.geometry import Point

from api.models.site import Site
from .base import BaseModel
from .camera_config import CameraConfig
from .recipe import Recipe
from .cross_section import CrossSection

map_template = """
<div id="id_geom_div_map" class="dj_map_wrapper">
<div id="map" class="dj_map" data-width="600" data-height="400" style="width: 600px; height: 400px;"></div>
</div>
<script>
    ol.proj.useGeographic();
    // add a feature
    
    const wkt = '{}';
    const wkt_profile = '{}';
    const format = new ol.format.WKT();
    const feature = format.readFeature(wkt);
    const feature_profile = format.readFeature(wkt_profile);
    const vector = new ol.layer.Vector({{
        source: new ol.source.Vector({{
            features: [feature],
        }}),
    }});

    const vector_profile = new ol.layer.Vector({{
        source: new ol.source.Vector({{
            features: [feature_profile],
        }}),
    }});
   
    const map = new ol.Map({{
        layers: [
            new ol.layer.Tile({{
                source: new ol.source.OSM(),
            }}), vector, vector_profile
        ],
        target: 'map',
        view: new ol.View({{
            center: [{}, {}],
            zoom: 18,
        }}),
    }});
</script>

"""

# Simple HTML template for non‑geographic x/y plot
vc_plot_3d_template = """
<div class="bbox-plot-wrapper">
    <img src="data:image/png;base64,{}" alt="3D camera config plot" />
</div>

"""

lens_position_schema = {
    'schema': 'http://json-schema.org/draft-07/schema#',
    'type': 'object',
    'properties': {
        'x': {
            'type': 'float'
        },
        'y': {
            'type': 'float'
        }
    },
    'required': ['x', 'y', 'z']
}


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

    @property
    def vc_plot_3d(self):
        """
        render a 3d plot with cross section and bbox in matplotlib,
        This does not use any geographic CRS; it just plots coordinates.
        """
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, projection="3d")
        # load cam config and cross section from data fields
        if not self.camera_config or not self.cross_section:
            return None
        camera_config = pyorc.CameraConfig(**self.camera_config.data)
        cs_data, crs = pyorc.cli.cli_utils.read_shape(geojson=self.cross_section.features)
        # coerce into a geopandas GeoDataFrame
        if crs is not None:
            geometry = [Point(_x, _y, _z) for _x, _y, _z in cs_data]
            cs_data = gpd.GeoDataFrame(geometry=geometry, crs=crs)
        cs = pyorc.CrossSection(camera_config=camera_config, cross_section=cs_data)
        camera_config.plot(ax=ax, mode="3d")
        cs.plot(ax=ax, h=cs.camera_config.gcps["h_ref"])
        # ax.set_xlabel("x")
        # ax.set_ylabel("y")
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(loc="best", fontsize=7)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpg", dpi=100, bbox_inches="tight")
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return mark_safe(vc_plot_3d_template.format(img_b64))

    vc_plot_3d.fget.short_description = "Camera calibration 3D view"

    @property
    def vc_view(self):
        if self.camera_config.bbox and self.camera_config.bbox.wkt:
            bbox_wkt = self.camera_config.bbox.wkt
        else:
            bbox_wkt = None
        # check for profiles
        if self.cross_section and getattr(self.cross_section, "multipoint", None) and self.cross_section.multipoint.wkt:
            profile_wkt = self.cross_section.multipoint.wkt
        else:
            profile_wkt = None
        if profile_wkt and bbox_wkt:
            return mark_safe(map_template.format(bbox_wkt, profile_wkt, self.camera_config.x, self.camera_config.y))
        elif bbox_wkt:
            # only plot cam config
            return mark_safe(map_template.format(bbox_wkt, "MULTIPOINT EMPTY", self.camera_config.x, self.camera_config.y))    
        else:
            return None
