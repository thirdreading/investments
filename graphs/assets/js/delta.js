var Highcharts;
var optionSelected;
var dropdown = $("#option_selector");
var url = document.getElementById("delta").getAttribute("url");
var url = document.getElementById("delta").getAttribute("variable");



// Build data selection menu
$.getJSON(url, function (source) {

		// Partition
    let partitions = source.partitions;
    var pa = partitions.indexOf('series_delta_%');

    // Data parts of ...
    let data = source.data[pa];

		// Menu
    for (var k = 0; k < (data.length - 1); k += 1) {
        dropdown.append($("<option></option>").attr("value", data[k].name).text(data[k].description));
    }

    // Load the first Option by default
    var defaultOption = dropdown.find("option:first-child").val();
    optionSelected = dropdown.find("option:first-child").text();

    // Generate
    generateChart(defaultOption);

});



// Dropdown
dropdown.on("change", function (e) {

    $("#option_selector_title").remove();

    // Save name and value of the selected option
    optionSelected = this.options[e.target.selectedIndex].text;
    var valueSelected = this.options[e.target.selectedIndex].value;

    //Draw the Chart
    generateChart(valueSelected);

});



// Generate graphs
function generateChart(fileNameKey) {

    $.getJSON(url, function (source){

        // https://api.highcharts.com/highstock/tooltip.pointFormat
        // https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/highcharts/demo/bubble
        // https://api.highcharts.com/highcharts/tooltip.headerFormat
        // https://www.highcharts.com/demo/stock/compare

        // Partition
        let partitions = source.partitions;
        var pa = partitions.indexOf('series_delta_%');

        // Data ...
        let calculations = source.data[pa];

        // Split
        for (var i = 0; i < calculations.length; i += 1) {

            if (calculations[i].name.match(fileNameKey)) {

                var seriesOptions = [];

                seriesOptions = {
                    name: calculations[i].description,
                    data: calculations[i].data
                };

            }

        }


        // Graphing
        Highcharts.setOptions({
            lang: {
                thousandsSep: ","
            }
        });

        Highcharts.chart("container0011", {

            chart: {
                type: "line",
                zoomType: "xy",
                marginTop: 105
            },

            title: {
                text: 'Delta<br>Percentages',
                style: {
                    "fontSize": "18px"
                }
            },
            subtitle: {
                text: '\nElement <b>' + fileNameKey + ' (' + description + ')</b> of<br>variable <b>' + variable + '</b>\n',
                style: {
                    "fontSize": "11px",
                    "fontWeight": "light"
                }
            },

            credits: {
                enabled: false
            },

            legend: {
                enabled: true,
                x: 15
            },

            xAxis: {
                title: {
                    text: "Year"
                },
                maxPadding: 0.05,
                gridLineWidth: 1
            },

            yAxis: {
                title: {
                    text: "Percentage"
                },
                maxPadding: 0.05,
                endOnTick: false
            },

            exporting: {
                buttons: {
                    contextButton: {
                        menuItems: ["viewFullscreen", "printChart", "separator",
                            "downloadPNG", "downloadJPEG", "downloadPDF", "downloadSVG", "separator",
                            "downloadXLS", "downloadCSV"],
                        x: 15
                    }
                }
            },

            tooltip: {
                shared: true,
                headerFormat: '<span style="font-size: 13px; color:{point.color}">\u25CF {point.x:,.2f}</span>',
                pointFormat: '<br/><p><br/>' +
                    '{series.name}: {point.y}<br/></p>' ,
                style: {
                    fontSize: "11px"
                }
            },

            plotOptions: {
                column: {
                    pointPadding: 0.1,
                    borderWidth: 0,
                    dataLabels: {
                        enabled: false
                    },
                    turboThreshold: 4000
                }
            },

            series: [{
                    type: "column",
                    name: seriesOptions.name,
                    data: seriesOptions.data
                }
            ]

        });

    }).fail(function () {
        console.log("Missing");
        $("#container0011").empty();
    });

}
