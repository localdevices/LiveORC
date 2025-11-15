from datetime import timedelta
import base64
import io
import matplotlib.pyplot as plt
import shapely.wkt
from django.contrib.auth import get_user_model
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy
from pyproj import CRS, Transformer
from shapely import ops

from api.models import BaseModel, Site, Server, Recipe, Profile
import pyorc


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
_bbox_plot_template = """
<div class="bbox-plot-wrapper">
    <img src="data:image/png;base64,{}" alt="Bounding box and profile plot" />
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
    """
    Contains JSON with a full camera configuration
    """
    def __str__(self):
        return f"{self.name} at {self.site.name}"
    name = models.CharField(max_length=100, help_text="Recognizable unique name for the camera configuration")
    camera_config = models.JSONField(
        null=True,
        blank=True,
        help_text="JSON fields containing a camera configuration, "
                  "see https://localdevices.github.io/pyorc/user-guide/camera_config/index.html for setup instructions"
    )
    allowed_dt = models.DurationField(
        "Allowed difference in time stamp",
        help_text="Maximum time difference allowed between a time stamp of an associated video, and a time series "
                  "instance at the associated site [sec]",
        default=timedelta(seconds=1800),
        validators=[
            MinValueValidator(timedelta(seconds=0)),
            MaxValueValidator(timedelta(seconds=86400))
        ]
    )
    start_date = models.DateTimeField("start validity date", auto_now_add=True)
    end_date = models.DateTimeField("end validity date", null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.CharField("pyORC version compatibility", max_length=15, blank=True, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    # user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    # TODO also connect to server
    # TODO connect to recipe and profile (where necessary)

    def clean(self):
        super().clean()
        # try:
        #     pyorc.CameraConfig(**self.camera_config)
        #     # see if you can make a camera config object
        # except BaseException as e:
        #     raise ValidationError(f"Problem with Camera Configuration: {e}")
        if self.profile:
            if self.profile.site != self.site:
                raise ValidationError(gettext_lazy("Profile site and Camera config site are not the same. Select a "
                                                   "profile with the same site as the camera configuration"))

    @property
    def crs(self):
        return CRS.from_user_input(self.camera_config["crs"])

    @property
    def bbox(self):
        if self.camera_config is not None:
            if "crs" in self.camera_config:
                crs = self.camera_config["crs"]
                transformer = Transformer.from_crs(
                    CRS.from_user_input(crs),
                    CRS.from_epsg(4326),
                    always_xy=True).transform

                polygon = shapely.wkt.loads(self.camera_config["bbox"])
                polygon = shapely.ops.transform(transformer, polygon)
                return GEOSGeometry(polygon.wkt, srid=4326)

    bbox.fget.short_description = "Polygon bounding box (wkt) for area of interest"

    @property
    def x(self):
        return self.bbox.centroid.x


    @property
    def y(self):
        return self.bbox.centroid.y


    @property
    def height(self):
        if self.camera_config is not None:
            return self.camera_config["height"]

    height.fget.short_description = "Height of frames [pix]"

    @property
    def width(self):
        if self.camera_config is not None:
            return self.camera_config["width"]

    width.fget.short_description = "Width of frames [pix]"

    def _bbox_plot_fallback(self):
        """
        Fallback: render a simple x/y plot with cross section and bbox in matplotlib,
        This does not use any geographic CRS; it just plots coordinates.
        """
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")
        # load cam config and cross section from data fields
        camera_config = pyorc.load_camera_config(self.data)
        cs = pyorc.CrossSection(camera_config=camera_config, cs=self.profile.data)
        camera_config.plot(ax=ax, mode="3d")
        cs.plot(ax=ax, mode="3d")
        # ax.set_xlabel("x")
        # ax.set_ylabel("y")
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(loc="best")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)
        img_b64 = base64.b64encode(buf.getvalue()).decode("ascii")
        return _bbox_plot_template.format(img_b64)


    @property
    def bbox_view(self):
        if self.bbox:
            try:
                bbox_wkt = self.bbox.wkt
            except Exception:
                bbox_wkt = None
        if self.profile and getattr(self.profile, "multipoint", None):
            try:
                profile_wkt = self.profile.multipoint.wkt
            except Exception:
                profile_wkt = None
        if bbox_wkt and profile_wkt:
            return mark_safe(
                map_template.format(self.bbox.wkt, self.profile.multipoint.wkt, self.x, self.y)
            )
        elif bbox_wkt:
            # only plot bounding box
            return mark_safe(
                map_template.format(
                    self.bbox.wkt,
                    'MULTIPOINT EMPTY',
                    self.x,
                    self.y
                )
            )
        else:
            #fallback to simple plot
            return mark_safe(self._bbox_plot_fallback())


    @property
    def resolution(self):
        if self.camera_config:
            return self.camera_config["resolution"]

    resolution.fget.short_description = "Resolution for orthorectification [m]"
    @property
    def window_size(self):
        if self.camera_config:
            return self.camera_config["window_size"]

    window_size.fget.short_description = "interrogation window size [pix]"

    @property
    def institute(self):
        return self.site.institute

