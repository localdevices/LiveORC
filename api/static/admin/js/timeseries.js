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
          animation: {
             onComplete: function(chart) {
                if (chart.initial){
                    updatePlot(t1, t2);
                }
             }
          },
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
                   suggestedMin: 0,
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
        url: endpoint,
        method: 'GET',
        dataType: 'json',
        data: {
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
    }, 200);
}
window.onload = function() {
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myLine = new Chart(ctx, config);
    // perform the first update of the data in the plot
    // Listen to the wheel, update plot once the wheel is done turning (after 0.2 seconds)
    document.getElementById('canvas').addEventListener('wheel', function(event) {
        handleWheelEvent();
    });
//    updatePlot(t1, t2);
};
