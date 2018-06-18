function drawBarChart(data, svg, value, color, maxValue) {
    var margin = {top: 50, right: 250, bottom: 50, left: 200},
        width = +svg.attr("width") - margin.left - margin.right,
        height = +svg.attr("height") - margin.top - margin.bottom,
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var median_single = calculateMedian(data, value);

    var medianData = [{"name": "personal Median", "value": median_single.toPrecision(2), "color": color},
        {"name": "overall Median", "value": median_all[value].toPrecision(2), "color": "#666967"}];

    var x = d3.scaleLinear()
        .domain([0, maxValue])
        .range([0, width]);

    var y = d3.scaleBand()
        .domain(medianData.map(function (d) {
            return d.name;
        }))
        .range([0, height])
        .paddingInner(0.1);

    var yAxis = d3.axisLeft()
        .scale(y)
        .tickSize(0);

    g.append("g")
        .attr("class", "barAnnotation")
        .call(yAxis);

    //Define Histogram
    var gLeft = g.append("g")
        .attr("class", "histogram");

    var yBar = gLeft.selectAll(".bar")
        .data(medianData)
        .enter()
        .append("g")
        .attr("fill", function (d) {
            return d.color
        });

    yBar.append("rect")
        .attr("class", "bar")
        .attr("y", function (d) {
            return y(d.name);
        })
        .attr("width", function (d) {
            if (d.value > maxValue) {
                return x(maxValue);
            } else {
                return x(d.value);
            }
        })
        .attr("height", y.bandwidth())
        .attr("fill", function (d) {
            return d.color
        });

    yBar.append("text")
        .attr("class", "barText")
        .attr("y", function (d) {
            return y(d.name) + y.bandwidth() / 2 + 4;
        })
        .attr("x", function (d) {
            if (d.value > maxValue) {
                return x(maxValue) + 20;
            } else {
                return x(d.value) + 20;
            }
        })
        .text(function (d) {
            return d.value;
        });
}

function redrawBarChart(data, svg, words, maxValue) {
    var margin = {top: 50, right: 250, bottom: 50, left: 250},
        width = +svg.attr("width") - margin.left - margin.right;

    var median_single = calculateMedian(data, words);

    var medianData = [median_single.toPrecision(2), median_all[words].toPrecision(2)];

    var x = d3.scaleLinear()
        .domain([0, maxValue])
        .range([0, width]);

    svg.selectAll("rect.bar")
        .data(medianData)
        .transition()
        .attr("width", function (d) {
            if (d > maxValue) {
                return x(maxValue)
            } else {
                return x(d)
            }
        });

    svg.selectAll("text.barText")
        .data(medianData)
        .transition()
        .attr("x", function (d) {
            if (d > maxValue) {
                return x(maxValue) + 20;
            } else {
                return x(d) + 20;
            }
        })
        .text(function (d) {
            return d;
        });
}
