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
var datapoints = [];
var config = {
    type: 'line',
    data: {
        datasets: [
            {
                label: 'Discharge',
//                type: 'line',
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
                data: datapoints,
                fill: "-1",
                pointRadius: 0,
                pointHoverRadius: 0,
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 0,
                tension: 0.1
            },
            {
                label: '25% low',
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
                data: datapoints,
                fill: "-1",
                pointRadius: 0,
                pointHoverRadius: 0,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgb(75, 192, 192)',
                borderWidth: 0,
                tension: 0.1
            },
        ]
    },
    options: {
        animation: {
            // perform the first update of the data in the plot
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
                min: 0,  // Set the minimum value for the y-axis
            }
        },
        plugins: {
            filler: {
                propagate: false
            },
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
    }
};
// restructure
function get_x_y(data, varname) {
    var output = [];
    data.forEach(function(d){
        output.push({x:d["timestamp"],y:d[varname]});
    });
    return output
}

function updatePlot(t1, t2) {
    $.ajax({
        url: endpoint,
        method: 'GET',
        dataType: 'json',
        data: {
          startDateTime: t1,
          endDateTime: t2,
//          format: "webjson"
        },
        success: function(data) {
            // Update only the data in the chart
            datapoints = data;
            data_05 = get_x_y(data, "q_05");
            data_25 = get_x_y(data, "q_25");
            data_75 = get_x_y(data, "q_75");
            data_95 = get_x_y(data, "q_95");
            data_median = get_x_y(data, "q_50");
            console.log(data_median);
            window.myLine.data.datasets[0].data = data_median;
            window.myLine.data.datasets[1].data = data_05;
            window.myLine.data.datasets[2].data = data_95;
            window.myLine.data.datasets[3].data = data_25;
            window.myLine.data.datasets[4].data = data_75;
            // Update the chart itself
            window.myLine.update();
        },
        error: function(error) {
            console.error('Error fetching plot data:', error);
        }
    });
}
var updateTimeout;
function handleZoomEvent() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(function() {
        var ts = get_xMinMax();
        console.log(ts);
        updatePlot(ts[0], ts[1]);
    }, 200);
}
function testZoomEvent() {
    clearTimeout(updateTimeout);
    updateTimeout = setTimeout(function() {
        alert("zoom event detected");
    }, 500);
}
window.onload = function() {
    var ctx = document.getElementById("canvas").getContext("2d");
    window.myLine = new Chart(ctx, config);
};
