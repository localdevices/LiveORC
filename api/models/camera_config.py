import base64
import io
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import pyorc
import shapely.ops
import shapely.wkt

from datetime import timedelta
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.html import mark_safe
from pyproj import CRS, Transformer

from .base import BaseModel
from .server import Server
from .site import Site

map_template = """
<div id="id_geom_div_map" class="dj_map_wrapper">
<div id="map" class="dj_map" data-width="600" data-height="400" style="width: 600px; height: 400px;"></div>
</div>
<script>
    ol.proj.useGeographic();
    const wkt = '{}';
    const format = new ol.format.WKT();
    const feature = format.readFeature(wkt);
    const vector = new ol.layer.Vector({{
        source: new ol.source.Vector({{
            features: [feature],
        }}),
    }});

    const map = new ol.Map({{
        layers: [
            new ol.layer.Tile({{
                source: new ol.source.OSM(),
            }}), vector
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
bbox_plot_3d_template = """
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


class CameraConfig(BaseModel):
    """Camera pose/calibration data used by VideoConfig."""

    name = models.CharField(max_length=100, help_text="Recognizable unique name for the camera configuration")
    data = models.JSONField(
        null=True,
        blank=True,
        help_text=(
            "JSON fields containing a camera configuration, "
            "see https://localdevices.github.io/pyorc/user-guide/camera_config/index.html for setup instructions"
        ),
    )
    allowed_dt = models.DurationField(
        "Allowed difference in time stamp",
        help_text=(
            "Maximum time difference allowed between an associated video time stamp and a "
            "time series instance at the associated site [sec]"
        ),
        default=timedelta(seconds=1800),
        validators=[MinValueValidator(timedelta(seconds=0)), MaxValueValidator(timedelta(seconds=86400))],
    )
    start_date = models.DateTimeField("start validity date", auto_now_add=True)
    end_date = models.DateTimeField("end validity date", null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.CharField("pyORC version compatibility", max_length=15, blank=True, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} at {self.site.name}"

    @property
    def crs(self):
        if self.data and "crs" in self.data:
            return CRS.from_user_input(self.data["crs"])

    @property
    def bbox(self):
        if self.data and "crs" in self.data and self.data["crs"] is not None and self.data.get("bbox"):
            transformer = Transformer.from_crs(
                CRS.from_user_input(self.data["crs"]),
                CRS.from_epsg(4326),
                always_xy=True,
            ).transform
            polygon = shapely.wkt.loads(self.data["bbox"])
            polygon = shapely.ops.transform(transformer, polygon)
            return GEOSGeometry(polygon.wkt, srid=4326)

    bbox.fget.short_description = "Polygon bounding box (wkt only) for area of interest"

    @property
    def x(self):
        return self.bbox.centroid.x if self.bbox else None

    @property
    def y(self):
        return self.bbox.centroid.y if self.bbox else None

    @property
    def height(self):
        if self.data:
            return self.data.get("height")

    height.fget.short_description = "Height of frames [pix]"

    @property
    def width(self):
        if self.data:
            return self.data.get("width")

    width.fget.short_description = "Width of frames [pix]"

    @property
    def bbox_plot_3d(self):
        """
        render a 3d plot with bbox and gcps in matplotlib,
        This does not use any geographic CRS; it just plots coordinates.
        """
        fig = plt.figure(figsize=(7, 5))
        ax = fig.add_subplot(111, projection="3d")
        # load cam config and cross section from data fields
        camera_config = pyorc.CameraConfig(**self.data)
        camera_config.plot(ax=ax, mode="3d")
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(loc="best", fontsize=7)

        buf = io.BytesIO()
        fig.savefig(buf, format="jpg", dpi=100, bbox_inches="tight")
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return mark_safe(bbox_plot_3d_template.format(img_b64))

    bbox_plot_3d.fget.short_description = "Camera calibration 3D view"


    @property
    def bbox_view(self):
        if self.bbox:
            return mark_safe(map_template.format(self.bbox.wkt, self.x, self.y))
        return None


    @property
    def resolution(self):
        if self.data:
            return self.data.get("resolution")

    resolution.fget.short_description = "Resolution for orthorectification [m]"

    @property
    def window_size(self):
        if self.data:
            return self.data.get("window_size")

    window_size.fget.short_description = "Interrogation window size [pix]"

    @property
    def institute(self):
        return self.site.institute
