from django.db import models
from django.contrib.gis.db import models as gismodels
from django.utils.html import mark_safe
from django.urls import reverse

from api.models import BaseModel

timeseries_template1 = """
	<div id="timeseries_chart" style="width: 600px; height: 400px;">
		<canvas id="canvas"></canvas>
	</div>
	<script>
	    function get_xMinMax() {
	        var xmin = window.myLine.scales["x"].min;
	        var xmax = window.myLine.scales["x"].max;
            dateMin = moment.unix(xmin/1000).format("YYYY-MM-DDTHH:MM");
            dateMax = moment.unix(xmax/1000).format("YYYY-MM-DDTHH:MM");
            return [dateMin, dateMax]
	    }

		function randomScalingFactor() {
			return Math.round(Math.random() * 100 * (Math.random() > 0.5 ? -1 : 1));
		}

		function randomColorFactor() {
			return Math.round(Math.random() * 255);
		}

		function randomColor(opacity) {
			return 'rgba(' + randomColorFactor() + ',' + randomColorFactor() + ',' + randomColorFactor() + ',' + (opacity || '.3') + ')';
		}

		function newDate(days) {
			return moment().add(days, 'd').toDate();
		}

		function newDateString(days) {
			return moment().add(days, 'h').format(timeFormat);
		}

		function newTimestamp(days) {
			return moment().add(days, 'd').unix();
		}

		function resetZoom() {
			window.myLine.resetZoom()
		}
		var timeFormat = 'YYYY-MM-DD HH:MM:SS';
        var datapoints = [{
            x: newDateString(-7),
            y: randomScalingFactor()
        }, {
            x: newDateString(-6),
            y: randomScalingFactor()
        }, {
            x: newDateString(-5),
            y: randomScalingFactor()
        }, {
            x: newDateString(-4.5),
            y: randomScalingFactor()
        }, {
            x: newDateString(-3),
            y: randomScalingFactor()
        }, {
            x: newDateString(-2),
            y: randomScalingFactor()
        }, {
            x: newDateString(-1),
            y: randomScalingFactor()
        }, {
            x: newDateString(0),
            y: randomScalingFactor()
        }];
        var config = {
              type: 'line',
              data: {
                datasets: [{
                  label: 'Discharge',
                  data: datapoints,
                  fill: false,
                  borderColor: 'rgb(75, 192, 192)',
                  tension: 0.1
                }]
              },
              options: {
                  scales: {
                       x: {
                            type: 'timeseries',
                            time: {
                            }
                       },
                       y: {
                        type: 'linear',
                        position: 'left',
                        ticks: {
                           suggestedMin: 0,    // minimum will be 0, unless there is a lower value.
                // OR //
//                            beginAtZero: true   // minimum value will be 0.
                        },
                        title: {
                          text: "Discharge [m3/s]",
                          display: true
                        },
//                        min: 0,  // Set the minimum value for the y-axis
//                        max: 100  // Set the maximum value for the y-axis
                        }
                      },
                plugins: {
                  zoom: {
                    limits: {
                      x: {min: '2023-10-01 00:00:00', max: '2023-11-30 00:00:00'},
                      y: {min: -200, max: 200, minRange: 50}
                    },
                    zoom: {
                      wheel: {
                        enabled: true,
                      },
                      pinch: {
                        enabled: true
                      },
                      mode: 'x',
                    },
                    pan: {
                      enabled: true,
                      mode: 'x'
                    }
                  }
                }
              }
            };
		function updatePlot(t1, t2) {
		    console.log(t1);
		    console.log(t2);
            $.ajax({
                url: '"""
timeseries_template2 = """',
                method: 'GET',
                dataType: 'json',
                data: {
                  fields: "timestamp,q_50",
                  startDateTime: t1,
                  endDateTime: t2,
                  format: "webjson"
                },
                success: function(data) {
                    // Update only the data in the chart
                    console.log(data);
//                    window.myLine.data.labels = data.x;
//                    window.myLine.data.datasets[0].data = data.y;
                    window.myLine.data.datasets[0].data = data;

                    // Update the chart
                    window.myLine.update();
                },
                error: function(error) {
                    console.error('Error fetching plot data:', error);
                }
            });
        }
        var updateTimeout;
        function handleWheelEvent() {
            clearTimeout(updateTimeout);
            updateTimeout = setTimeout(function() {
                var ts = get_xMinMax();
                console.log(ts);
                updatePlot(ts[0], ts[1]);
            }, 1000);
        }
        window.onload = function() {
        var ctx = document.getElementById("canvas").getContext("2d");
        window.myLine = new Chart(ctx, config);
        document.getElementById('canvas').addEventListener('wheel', function(event) {
            handleWheelEvent();
            // Handle zoom event (e.g., adjust axis ranges)
            // Then, update only the data in the plot
//            updatePlot(String(ts[0]), String(ts[1]));

        });
    };

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
        uri = reverse("api:site-timeseries-list", args=([f"{self.id}"]))
        return mark_safe(timeseries_template1 + uri + timeseries_template2)
