from datetime import timedelta
import shapely.wkt
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, BaseValidator
from django.utils.html import mark_safe
from pyproj import CRS, Transformer
from shapely import ops

from ..models import Site, Server, Recipe, Profile, validators
import pyorc


map_template = """
<div id="id_geom_div_map" class="dj_map_wrapper">
<div id="map" class="dj_map" data-width="600" data-height="400" style="width: 600px; height: 400px;"></div>
</div>
<script>
    ol.proj.useGeographic();
    // add a feature
    
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

class CameraConfig(models.Model):
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
    version = models.CharField("pyORC version compatibility", max_length=15, blank=True, default=pyorc.__version__, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO also connect to server
    # TODO connect to recipe and profile (where necessary)

    def clean(self):
        super().clean()
        try:
            pyorc.CameraConfig(**self.data)
            # see if you can make a camera config object
        except BaseException as e:
            raise ValidationError(f"Problem with Camera Configuration: {e}")

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
    def height(self):
        if self.camera_config is not None:
            return self.camera_config["height"]

    height.fget.short_description = "Height of frames [pix]"

    @property
    def width(self):
        if self.camera_config is not None:
            return self.camera_config["width"]

    width.fget.short_description = "Width of frames [pix]"

    @property
    def bbox_view(self):
        return mark_safe(
            map_template.format(self.bbox.wkt, self.site.geom.x, self.site.geom.y)
        )

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

