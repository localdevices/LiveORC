from datetime import timedelta

from django.db import models
from django.contrib.gis.db import models as gismodels
from django.utils.html import mark_safe
from django.urls import reverse

from api.models import BaseModel

timeseries_template1 = """
	<div class="slidecontainer">
        <p>Set filter for optically resolved percentage. Higher means only well-illuminated videos are shown</p>
        <input type="range" min="1" max="100" value="60" class="slider" id="fractionRange" onchange="updateLines()">
    </div>
	<div id="timeseries_chart" style="width: 600px; height: 400px;">
		<canvas id="canvas"></canvas>
	</div>
	<script>
	    var endpoint = "{}";
	    var t1 = {};
	    var t2 = {};
	    var t_last = {};
	    var video_prefix = "/admin/api/video/"
	</script>
"""

class Site(BaseModel):
    """
    Location of one or more videos
    """
    def __str__(self):
        return "{:s} at lon: {:0.1f}, lat: {:0.1f}".format(self.name, self.geom.x, self.geom.y)

    name = models.CharField(max_length=100, help_text="Recognizable unique name for your site")
    geom = gismodels.PointField("Location", srid=4326, help_text="Approximate location of the site")

    @property
    def timeseries_chart(self):
        # find out what the end date should be
        from api.models import TimeSeries
        timeseries_last = TimeSeries.objects.filter(site=self.id).last()
        print(timeseries_last.timestamp)
        t1 = (timeseries_last.timestamp - timedelta(days=1)).timestamp()*1000
        t2 = timeseries_last.timestamp.timestamp()*1000

        uri = reverse("api:site-timeseries-list", args=([f"{self.id}"]))
        timeseries_html = timeseries_template1.format(uri, t1, t2, t2)
        return mark_safe(timeseries_html)
