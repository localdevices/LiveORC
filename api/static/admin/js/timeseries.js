function get_xMinMax() {
    var xmin = window.myLine.scales["x"].min;
    var xmax = window.myLine.scales["x"].max;
    return [xmin, xmax]
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
var datapoints = [];
var data_05 = [];
var data_25 = [];
var data_75 = [];
var data_95 = [];
var data_median = [];
var data_h = [];
var chartInitial = true;

var config = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Discharge',
//                type: 'time',
                data: datapoints,
                fill: false,
                pointRadius: 1,
                backgroundColor: 'rgb(255, 255, 255)',
                pointHoverRadius: 3,
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 1,
                tension: 0.1
            },
            {
                label: '5% low',
//                type: 'time',
                data: datapoints,
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0,
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 0,
                tension: 0.1
            },
            {
                label: '5-95% confidence',
//                type: 'time',
                data: datapoints,
                fill: "-1",
                pointRadius: 0,
                pointHoverRadius: 0,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 0,
                tension: 0.1
            },
            {
                label: '25% low',
//                type: 'time',
                data: datapoints,
                fill: false,
                pointRadius: 0,
                pointHoverRadius: 0,
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 0,
                tension: 0.1
            },
            {
                label: '25-75% confidence',
//                type: 'time',
                data: datapoints,
                fill: "-1",
                pointRadius: 0,
                pointHoverRadius: 0,
                backgroundColor: 'rgba(75, 192, 192, 0.3)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 0,
                tension: 0.1
            },
            {
                label: 'Water level',
//                type: 'time',
                data: datapoints,
                fill: false,
                pointRadius: 1,
                pointHoverRadius: 3,
                backgroundColor: 'rgb(255, 255, 255)',
                borderColor: 'rgb(255, 50, 50)',
                borderWidth: 1,
                tension: 0.1,
                yAxisID: "y1"
            },
        ]
    },
    options: {
        responsiveAnimationDuration: 0,
        animation: {
//            duration: 0,
            // perform the first update of the data in the plot
            onComplete: function(chart) {
                if (chartInitial){
                    console.log("updating chart")
                    updatePlot(t1, t2);
                    window.myLine.config.options.scales.x.min = t1;
                    window.myLine.config.options.scales.x.max = t2;
                    window.myLine.update();
                    chartInitial = false
                    window.myLine.config.options.animation.duration = 0;

                }
            }
        },
        scales: {
            x: {
                type: 'time',
                time: {
                }
//                min: t1
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
                min: 0,  // Set the minimum value for the y-axis
            },
            y1: {
                type: 'linear',
                position: 'right',
                title: {
                    text: "Water level [m]",
                    display: true
                },
            }

        },
        plugins: {
            filler: {
                propagate: false
            },
            zoom: {
                limits: {
//                    x: {min: '2023-10-01 00:00:00', max: '2023-11-30 00:00:00'},
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
                    // Listen to the wheel, update plot once the wheel is done turning (after 0.2 seconds)
                    onZoomComplete({chart}) {
                        handleZoomEvent();
                    }
                },
                pan: {
                    enabled: true,
                    mode: 'x'
                }
            },
            legend: {
//                display: false,
                labels: {
                    filter: function(item, chart) {
                        // Logic to remove a particular legend item goes here

                        return !item.text.includes('25% low') & !item.text.includes('5% low');
                    }
                }
            }
        },
        onClick: function (event, elements) {
            if (elements && elements.length > 0) {
                // Get the index of the clicked point
                var index = elements[0].index;
                url = window.myLine.data.datasets[0].data[index]["url"]
                if (url.slice(url.length-4,url.length) == "null") {
                    alert("Video analysis not available for this timestamp")
                }
                else {
                // Open the URL in a new tab or window
                    window.open(url, '_blank');
                }
            }
        }
    }
};
// restructure
function get_x_y(data, varname, fraction, add_link) {
    var output = [];
    if (add_link){
        data.forEach(function(d){
            if (d["fraction_velocimetry"] >= fraction){
                output.push({
                    x:d["timestamp"].slice(0,10) + " " + d["timestamp"].slice(11,16),
                    y:d[varname],
                    url: video_prefix + d["video"]
                });
            } else {
                output.push({
                    x:d["timestamp"].slice(0,10) + " " + d["timestamp"].slice(11,16),
                    y:Number.NaN
                });
            }
        });
    } else {
        data.forEach(function(d){
            if (d["fraction_velocimetry"] >= fraction){
                output.push({
                    x:d["timestamp"].slice(0,10) + " " + d["timestamp"].slice(11,16),
                    y:d[varname]
                });
            } else {
                output.push({
                    x:d["timestamp"].slice(0,10) + " " + d["timestamp"].slice(11,16),
                    y:Number.NaN
                });
            }
        });
    }
    return output
}

function updatePlot(t1, t2) {

    dateMin = moment.unix((t1-10*1000*86400)/1000).format("YYYY-MM-DDTHH:MM");
    dateMax = moment.unix((t2+10*1000*86400)/1000).format("YYYY-MM-DDTHH:MM");
    $.ajax({
        url: endpoint,
        method: 'GET',
        dataType: 'json',
        data: {
          startDateTime: dateMin,
          endDateTime: dateMax,
//          format: "webjson"
        },
        success: function(data) {
            // Update only the data in the chart
            datapoints = data;
            updateLines();
//            data_05 = get_x_y(data, "q_05", fraction, false);
//            data_25 = get_x_y(data, "q_25", fraction, false);
//            data_75 = get_x_y(data, "q_75", fraction, false);
//            data_95 = get_x_y(data, "q_95", fraction, false);
//            data_median = get_x_y(data, "q_50", fraction, true);
//            window.myLine.data.datasets[0].data = data_median;
//            window.myLine.data.datasets[1].data = data_05;
//            window.myLine.data.datasets[2].data = data_95;
//            window.myLine.data.datasets[3].data = data_25;
//            window.myLine.data.datasets[4].data = data_75;
//            // Update the chart itself
//            window.myLine.update()
        },
        error: function(error) {
            console.error('Error fetching plot data:', error);
        }
    });
}
function updateLines() {
    fraction = parseInt(document.getElementById("fractionRange").value);
    data_05 = get_x_y(datapoints, "q_05", fraction, false);
    data_25 = get_x_y(datapoints, "q_25", fraction, false);
    data_75 = get_x_y(datapoints, "q_75", fraction, false);
    data_95 = get_x_y(datapoints, "q_95", fraction, false);
    data_h = get_x_y(datapoints, "h", 0, false);
    data_median = get_x_y(datapoints, "q_50", fraction, true);
    window.myLine.data.datasets[0].data = data_median;
    window.myLine.data.datasets[1].data = data_05;
    window.myLine.data.datasets[2].data = data_95;
    window.myLine.data.datasets[3].data = data_25;
    window.myLine.data.datasets[4].data = data_75;
    window.myLine.data.datasets[5].data = data_h;
    // Update the chart itself
    window.myLine.update()
}

var updateTimeout;
function handleZoomEvent() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(function() {
        // assume we need to update first
        var replot = true
        var ts = get_xMinMax();
        if (datapoints.length > 0){
            // check if first date in datapoints is before dateMin or last date is after dateMax
            t1 = moment(datapoints[0]["timestamp"]).unix()*1000
            t2 = moment(datapoints[datapoints.length - 1]["timestamp"]).unix()*1000
            replot = (ts[0] < t1) || ((ts[1] > t2) && (t2 < t_last))
        }
        if (replot) {
            console.log("Requested data is beyond current span, reloading...")
            updatePlot(ts[0], ts[1]);
        }
    }, 200);
}
//window.onload = function() {
//    var ctx = document.getElementById("canvas").getContext("2d");
//    canvas = document.getElementById("canvas")
//    window.myLine = new Chart(ctx, config);
//
//};

function visualize(){
    console.log("Visualizing time series")
    var ctx = document.getElementById("canvas").getContext("2d");
    canvas = document.getElementById("canvas")
    window.myLine = new Chart(ctx, config);

}