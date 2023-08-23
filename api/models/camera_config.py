# from django.db import models
import shapely.wkt
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, BaseValidator
from pyproj import CRS, Transformer
from shapely import ops

from ..models import Site, Server, Recipe, Profile, validators
import jsonschema

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
    height = models.IntegerField(help_text="Height of the image frame in nr. of pixels")
    width = models.IntegerField(help_text="Width of the image frame in nr. of pixels")
    crs_wkt = models.CharField(
        max_length=2000,
        help_text="Well-known text or EPSG code for the camera configuration. If set, it must be a metre projection type",
        null=True,
        blank=True
    )
    resolution = models.FloatField(
        validators=[MinValueValidator(0.001), MaxValueValidator(0.1)],
        default=0.03,
        help_text="Resolution of the planar reprojected image over the bounding box of interest. For small streams like 1 meter, this may be as low as 0.001 or 0.002, for large 100m streams with large scale patterns, a value of 0.05 is recommended.",
    )
    window_size = models.IntegerField(
        validators=[MinValueValidator(5), MaxValueValidator(50)],
        help_text="Amount of pixels to use to find patterns in, typically a value of 15 or 20 is good.",
        default=15
    )
    lens_position = models.JSONField(
        validators=[validators.JSONSchemaValidator(limit_value=lens_position_schema)],
        null=True,
        blank=True,
        editable=False
    )

    gcps = models.JSONField(
        help_text='Ground control points and vertical reference as JSON. Must contain fields "src", "dst", "h_ref", "z_0" and may contain field "crs".'
    )
    is_nadir = models.BooleanField(
        default=False,
        editable=False,
        help_text="If set, the video is assumed to be taken at nadir, making it possible to orthorectify with only 2 points."
    )
    camera_calibration = models.JSONField(
        null=True,
        blank=True,
        editable=False,
        help_text="Intrinsic matrix, stabilization and distortion parameters of the camera, defining the objective size, center and focal length, lens distortion and polygon of non-moving areas."
    )
    # stabilize = models.JSONField(
    #     null=True,
    #     blank=True,
    #     help_text="Polygon, that bounds the water surface. Area outside is used to define stabilization region."
    # )
    bbox_wkt = models.CharField(max_length=2000, editable=False)
    bbox = models.PolygonField(srid=4326, help_text="Polygon in lat-lon for display purposes", null=True) #, editable=False)

    # data = models.JSONField(help_text="JSON fields containing a camera configuration, see https://localdevices.github.io/pyorc/user-guide/camera_config/index.html for setup instructions")
    start_date = models.DateTimeField("start validity date", auto_now_add=True)
    end_date = models.DateTimeField("end validity date", null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    version = models.CharField(max_length=15, blank=True, default=pyorc.__version__, editable=False)
    server = models.ForeignKey(Server, on_delete=models.SET_NULL, null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True, blank=True)
    profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    # TODO also connect to server
    # TODO connect to recipe and profile (where necessary)
    def save(self):
        super().save()

    # def clean(self):
    #     super().clean()
    #     try:
    #         pyorc.CameraConfig(**self.data)
    #         # see if you can make a camera config object
    #     except BaseException as e:
    #         raise ValidationError(f"Problem with Camera Configuration: {e}")

    @property
    def crs(self):
        return CRS.from_user_input(self.crs_wkt)

    # @property
    # def bbox(self):
    #     self.crs
    #     transformer = Transformer.from_crs(
    #         self.crs,
    #         CRS.from_epsg(4326),
    #         always_xy=True).transform
    #     polygon = shapely.wkt.loads(self.bbox_wkt)
    #     polygon = ops.transform(transformer, polygon)
    #     return GEOSGeometry(polygon.wkt, srid=4326)
