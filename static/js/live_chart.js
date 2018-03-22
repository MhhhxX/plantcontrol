const dataPrecision = 20;
var pause = false;
var myBar = null;

function initDataList() {
    var values = [];
    for (var i = 0; i<dataPrecision; i++) {
        values.push(0.0);
    }
    return values;
}

function initTimeList() {
    var values = [];
    for (var i = 0; i < dataPrecision; i++) {
        values.push("00:00:00");
    }
    return values;
}

function resize(event){
    var chart = $("#chart");
    var chartContainer = $(chart).parent();
    var windowHeight = Math.floor(window.innerHeight.valueOf());

    // orientation handling for mobile devices
    if ($(window).width() < 768) {
        if (event.orientation === 'portrait') {
            $(chartContainer).css('height', 0.6 * windowHeight + "px");
        }
        else
            $(chartContainer).css('height', 0.95 * windowHeight + "px");
    } // desktop
    else
        $(chartContainer).css('height', 0.6 * windowHeight + "px");

    if (myBar == null)
        $(chartContainer).css("min-width", (50 * dataPrecision) + "px");

}

function generateFixedAxis(myBar) {
    var sourceCanvas = myBar.chart.canvas;
    var copyWidthAx1 = myBar.scales['y-axis-1'].width - 10;
    var copyHeightAx1 = myBar.scales['y-axis-1'].height + myBar.scales['y-axis-1'].top + 10;
    var copyWidthAx2 = myBar.scales['y-axis-2'].width - 10;
    var copyHeightAx2 = myBar.scales['y-axis-2'].height + myBar.scales['y-axis-2'].top + 10;
    var xSrcAx2 = sourceCanvas.width;
    var destXAx2 = $(".canvas-wrapper").width() - copyWidthAx2;
    var targetCtx1 = document.getElementById("fixed-chart-axis-1").getContext("2d");
    var targetCtx2 = document.getElementById("fixed-chart-axis-2").getContext("2d");
    targetCtx1.canvas.width = copyWidthAx1;
    targetCtx1.canvas.height = sourceCanvas.height;
    targetCtx2.canvas.width = $(".canvas-wrapper").width();
    targetCtx2.canvas.height = sourceCanvas.height;
    targetCtx1.clearRect(0, 0, targetCtx1.canvas.width, targetCtx1.canvas.height);
    if ($(window).width() < 768) {
        targetCtx1.drawImage(sourceCanvas, 0, 0, 3 * copyWidthAx1, 3 * copyHeightAx1, 0, 0, copyWidthAx1, copyHeightAx1);
        targetCtx2.drawImage(sourceCanvas, xSrcAx2 - 3 * copyWidthAx2, 0, 3 * copyWidthAx2, 3 * copyHeightAx2, destXAx2, 0, copyWidthAx2, copyHeightAx2);
    } else {
        targetCtx1.drawImage(sourceCanvas, 0, 0, copyWidthAx1, copyHeightAx1, 0, 0, copyWidthAx1, copyHeightAx1);
        targetCtx2.drawImage(sourceCanvas, xSrcAx2 - copyWidthAx2, 0, copyWidthAx2, copyHeightAx2, destXAx2, 0, copyWidthAx2, copyHeightAx2);
    }
}

var barChartData = {
    labels: initTimeList(),
    datasets: [{
        label: 'Temperature',
        backgroundColor: 'rgba(255, 165, 0, 0.5)',
        borderColor: 'rgba(255, 165, 0, 0.7)',
        yAxisID: "y-axis-1",
        fill: false,
        data: initDataList()
    }, {
        label: 'Humidity',
        backgroundColor: 'rgba(51, 102, 255, 0.5)',
        borderColor: 'rgba(51, 102, 255, 0.7)',
        yAxisID: "y-axis-2",
        fill: false,
        data: initDataList()
    }]
};

$(document).ready(function () {
    $("#chart-pause").click(function () {
        if($(this).text() === 'pause') {
            $(this).html('<i class="material-icons">play_arrow</i>');
            pause = true;
        } else {
            $(this).html('<i class="material-icons">pause</i>');
            pause = false;
            updateChart();
        }
    });

    function updateChart() {
        $.ajax({
        type: 'GET',
        url: 'update_chart',
        dataType: "json",
        data: {
           "update_chart": "True"
        }
        }).success(function (data) {
            myBar.data.labels.splice(0, 1);
            myBar.data.labels.push(data['time']);
            myBar.data.datasets[0].data.splice(0, 1);
            myBar.data.datasets[1].data.splice(0, 1);
            myBar.data.datasets[0].data.push(parseFloat(data['temperature']));
            myBar.data.datasets[1].data.push(parseFloat(data['humidity']));
            myBar.update();
            $("#temperature").text(data['temperature']);
            $("#humidity").text(data['humidity']);
        }).complete(function (data) {
            if (!pause)
                setTimeout(function () {
                    updateChart();
                }, 3000)
        });
    }
    var evt = Math.abs(parseInt(window.orientation)) === 0 ? {orientation: 'portrait'} : {orientation: 'landscape'};
    resize(evt);

    $(window).on('orientationchange', function(event) {
        var orientation = Math.abs(parseInt(window.orientation)) === 0 ? {orientation: 'portrait'} : {orientation: 'landscape'};

        var orientationChange = function(evt) {
            resize(orientation);
            generateFixedAxis(myBar);
            $(window).off('resize', orientationChange);
        };
        $(window).on('resize', orientationChange);
    });

    var ctx = document.getElementById("chart").getContext("2d");
    myBar = new Chart(ctx, {
        type: 'line',
        data: barChartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            events: ["click"],
            title: {
                display: true,
                text: "Temperature, Humidity Live Chart"
            },
            tooltips: {
                mode: 'index',
                intersect: true,
                callbacks: {
                    label: function (tooltipItem, data) {
                            var label = data.datasets[tooltipItem.datasetIndex].label || '';
                            if (label)
                                label += ': ';
                            if (tooltipItem.datasetIndex === 0)
                                return label  + tooltipItem.yLabel + "°C";
                            else
                                return label + tooltipItem.yLabel + "%";
                    }
                }
            },
            scales: {
                yAxes: [{
                    type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: "left",
                    id: "y-axis-1",
                    ticks: {
                        min: 5,
                        max: 90,
                        stepSize: 5,
                        callback: function (value, index, values) {
                            return value + "°C";
                        }
                    }
                }, {
                    type: "linear", // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
                    display: true,
                    position: "right",
                    id: "y-axis-2",
                    ticks: {
                        min: 5,
                        max: 90,
                        stepSize: 5,
                        callback: function (value, index, values) {
                            return value + "%";
                        }
                    },
                    gridLines: {
                        //drawOnChartArea: false
                        borderDash: [5, 15]
                    }
                }]
            },

            animation: {
                onComplete: function (animation) {
                    generateFixedAxis(myBar);
                }
            }
        }
    });

    updateChart();

});