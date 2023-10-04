from django.db import models
from django.contrib.gis.db import models as gismodels
from .institution import Institution


class Site(gismodels.Model):
    """
    Location of one or more videos
    """
    def __str__(self):
        return "{:s} at lon: {:0.1f}, lat: {:0.1f}".format(self.name, self.geom.x, self.geom.y)

    name = models.CharField(max_length=100, help_text="Recognizable unique name for your site")
    geom = gismodels.PointField("Location", srid=4326, help_text="Approximate location of the site")
    institution = models.ForeignKey(Institution, blank=True, null=True, on_delete=models.CASCADE)

