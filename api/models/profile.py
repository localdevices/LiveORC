import pyorc
import shapely
import shapely.geometry

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.html import mark_safe

from pyproj import CRS, Transformer

from ..models import Site

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


class Profile(models.Model):
    """
    Contains the river profile as a geojson
    """
    name = models.CharField(max_length=100, help_text="Recognizable unique name for your profile")
    data = models.JSONField(help_text="GeoJSON fields containing Point (x,y,z) geometries that encompass a cross section")
    timestamp = models.DateTimeField("survey date", default=timezone.now)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)

    # def clean(self):
    #     super().clean()
    #     try:
    #         pyorc.cli.cli_utils.read_shape(geojson=self.data)
    #         # see if you can make a camera config object
    #     except BaseException as e:
    #         raise ValidationError(f"Problem with Profile data: {e}")

    def __str__(self):
        return f"{self.name} at {self.site.name}"
    # TODO: change into a GeoJSON field (using GeoDjango)
    @property
    def coords(self):
        data, crs = pyorc.cli.cli_utils.read_shape(geojson=self.data)
        return data

    @property
    def crs(self):
        return CRS.from_user_input(self.data["crs"]["properties"]["name"])

    @property
    def multipoint(self):
        if self.crs is not None:
            crs = self.crs
            transformer = Transformer.from_crs(
                crs,
                CRS.from_epsg(4326),
                always_xy=True).transform
            multipoint = shapely.geometry.MultiPoint(self.coords)
            multipoint = shapely.ops.transform(transformer, multipoint)
            return GEOSGeometry(multipoint.wkt, srid=4326)

    multipoint.fget.short_description = "Cross section points (wkt) for profile measurements"

    @property
    def profile_view(self):
        return mark_safe(
            map_template.format(self.multipoint.wkt, self.site.geom.x, self.site.geom.y)
        )
