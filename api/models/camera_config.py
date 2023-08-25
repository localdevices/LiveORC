# from django.db import models
import shapely.wkt
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, BaseValidator
from django.utils.html import mark_safe
from pyproj import CRS, Transformer
from shapely import ops

from ..models import Site, Server, Recipe, Profile, validators
import jsonschema

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

import pyorc

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
    # height = models.IntegerField(help_text="Height of the image frame in nr. of pixels")
    # width = models.IntegerField(help_text="Width of the image frame in nr. of pixels")
    # crs_wkt = models.CharField(
    #     max_length=2000,
    #     help_text="Well-known text or EPSG code for the camera configuration. If set, it must be a metre projection type",
    #     null=True,
    #     blank=True
    # )
    # resolution = models.FloatField(
    #     validators=[MinValueValidator(0.001), MaxValueValidator(0.1)],
    #     default=0.03,
    #     help_text="Resolution of the planar reprojected image over the bounding box of interest. For small streams like 1 meter, this may be as low as 0.001 or 0.002, for large 100m streams with large scale patterns, a value of 0.05 is recommended.",
    # )
    # window_size = models.IntegerField(
    #     validators=[MinValueValidator(5), MaxValueValidator(50)],
    #     help_text="Amount of pixels to use to find patterns in, typically a value of 15 or 20 is good.",
    #     default=15
    # )
    # lens_position = models.JSONField(
    #     validators=[validators.JSONSchemaValidator(limit_value=lens_position_schema)],
    #     null=True,
    #     blank=True,
    #     editable=False
    # )
    #
    # gcps = models.JSONField(
    #     help_text='Ground control points and vertical reference as JSON. Must contain fields "src", "dst", "h_ref", "z_0" and may contain field "crs".'
    # )
    # is_nadir = models.BooleanField(
    #     default=False,
    #     editable=False,
    #     help_text="If set, the video is assumed to be taken at nadir, making it possible to orthorectify with only 2 points."
    # )
    # camera_calibration = models.JSONField(
    #     null=True,
    #     blank=True,
    #     editable=False,
    #     help_text="Intrinsic matrix, stabilization and distortion parameters of the camera, defining the objective size, center and focal length, lens distortion and polygon of non-moving areas."
    # )
    # # stabilize = models.JSONField(
    # #     null=True,
    # #     blank=True,
    # #     help_text="Polygon, that bounds the water surface. Area outside is used to define stabilization region."
    # # )
    # bbox_wkt = models.CharField(max_length=2000, editable=False)
    # bbox = models.PolygonField(srid=4326, help_text="Polygon in lat-lon for display purposes", null=True) #, editable=False)
    camera_config = models.JSONField(null=True, blank=True)

    # data = models.JSONField(help_text="JSON fields containing a camera configuration, see https://localdevices.github.io/pyorc/user-guide/camera_config/index.html for setup instructions")
    start_date = models.DateTimeField("start validity date", auto_now_add=True)
    end_date = models.DateTimeField("end validity date", null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.CharField("pyORC version copmpatibility", max_length=15, blank=True, default=pyorc.__version__, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO also connect to server
    # TODO connect to recipe and profile (where necessary)

    # def clean(self):
    #     super().clean()
    #     try:
    #         pyorc.CameraConfig(**self.data)
    #         # see if you can make a camera config object
    #     except BaseException as e:
    #         raise ValidationError(f"Problem with Camera Configuration: {e}")

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
        return self.camera_config["resolution"]

    resolution.fget.short_description = "Resolution for orthorectification [m]"
    @property
    def window_size(self):
        return self.camera_config["window_size"]

    window_size.fget.short_description = "interrogation window size [pix]"

    # @property
    # def camera_config(self):
    #     """
    #
    #     Returns
    #     -------
    #     camera config dict as it should be forwarded to pyOpenRiverCam
    #     """
    #     if self.lens_position is not None:
    #         lens_position = [self.lens_position["x"], self.lens_position["y"], self.lens_position["z"]]
    #     else:
    #         lens_position = None
    #     cam_config = dict(
    #         height=self.height,
    #         width=self.width,
    #         gcps=self.gcps,
    #         bbox=self.bbox_wkt,
    #         lens_position=lens_position,
    #         crs=self.crs_wkt,
    #         is_nadir=self.is_nadir,
    #         window_size=self.window_size,
    #         resolution=self.resolution,
    #         **self.camera_calibration
    #     )
    #     return cam_config
