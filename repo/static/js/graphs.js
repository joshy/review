$(function () {
    var counter = 0;
    if ('dashboard' == $('body').data('page')) {
        console.log('on dashboard page');
        checkboxHandler();
        d3.csv(data_url(), function (error, data) {
            if (error) throw error;

            drawSimilarityGraph(data);
            drawWordsAddedGraph(data);
            drawWordsDeletedGraph(data);
        });
    }

    function data_url() {
        var writer = $('#writer').val(),
            last_exams = $('#last_exams').val(),
            start_date = $('#start_date').val(),
            end_date = $('#end_date').val(),
            departments = [];

        $.each($("input[name='departments']:checked"), function () {
            departments.push($(this).val());
        });

        var param = {
            'w': writer,
            'last_exams': last_exams,
            'start_date': start_date,
            'end_date': end_date,
            'departments': departments
        };
        return 'dashboard/data?' + $.param(param)
    }

    function drawSimilarityGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            pieSegments = [
                {name: 'medianValue', value: 0.0, color: "steelblue"},
                {name: 'maxValue', value: 0.0, color: 'lightgrey'},
            ],
            classNames = ["barSimilarity", "buttonSimilarity", "buttonAnnotationSimilarity", "Similarity"],
            color = "steelblue",
            radius = 150;

        drawGraph(data, d3.select("#SimilarityGraph"), "jaccard_s_f", maxIntervalValue, minIntervalValue, classNames, color, radius, pieSegments);
        drawPieChart(d3.select("#SimilarityPieChartSingle"), median_single["jaccard_s_f"], "pieChartFontSingle", radius, pieSegments);
        pieSegments[0].color = "#666967";
        drawPieChart(d3.select("#SimilarityPieChartAll"), median_all["jaccard_s_f"], "pieChartFontAll", radius, pieSegments);
    }

    function drawWordsAddedGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            maxBarValue = 1,
            classNames = ["barWordsAdded", "buttonWordsAdded", "buttonAnnotationWordsAdded", "Words"],
            color = "green";
        drawGraph(data, d3.select("#WordsAddedGraph"), "words_added_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue);
        drawBarChart(d3.select("#WordsAddedBarChart"), "words_added_relative_s_f", color, maxBarValue);
    }

    function drawWordsDeletedGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            maxBarValue = 1,
            classNames = ["barWordsDeleted", "buttonWordsDeleted", "buttonAnnotationWordsDeleted", "Words"],
            color = "red";
        drawGraph(data, d3.select("#WordsDeletedGraph"), "words_deleted_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue);
        drawBarChart(d3.select("#WordsDeletedBarChart"), "words_deleted_relative_s_f", color, maxBarValue);

    }

    function drawGraph(data, svg, value, maxIntervalValue, minIntervalValue, classNames, color, specificValue, pieSegments) {
        var margin = {top: 50, right: 20, bottom: 150, left: 45},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            gap = 170,
            g = svg.append("g")
                .attr("class", "graphArea")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")"),
            brushArea = svg.append("g")
                .attr("class", "brushArea")
                .attr("transform", "translate(" + margin.left + "," + (height + margin.bottom - margin.top / 10) + ")"),

            formatTime = d3.timeFormat("%d.%m"),
            brush = d3.brushX()
                .extent([[gap + margin.right, -margin.bottom / 3], [width, 1]])
                .on("brush", brushed),


            //Define Axes
            x = d3.scaleTime().range([gap + margin.right, width]),
            x2 = d3.scaleTime().range([gap + margin.right, width]),
            y = d3.scaleLinear().range([height, 0]).domain([minIntervalValue, maxIntervalValue]),
            yx = d3.scaleLinear().range([0, gap]);

        //Draw Gridlines
        g.append("g")
            .attr("class", "grid")
            .call(d3.axisLeft(y)
                .ticks(4)
                .tickSize(-width)
                .tickFormat("")
            );

        //Define Histogramm
        var gLeft = g.append("g")
            .attr("class", "histogram");

        //Define the div for the tooltip
        var div = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        //Get Data
        data.forEach(function (data) {
            data[value] = +data[value];
            data.unters_beginn = new Date(data.unters_beginn);
        });

        x.domain(d3.extent(data, function (d) {
            return d.unters_beginn;
        }));

        x2.domain(x.domain());

        //Draw ExceedingLine
        g.append("line")
            .attr("class", "exceedingLine")
            .attr("x1", 0)
            .attr("y1", -margin.top / 3)
            .attr("x2", width)
            .attr("y2", -margin.top / 3);

        //Draw ExceedingLineText
        g.append("text")
            .attr("class", "exceedingLineAnnotation")
            .attr("fill", color)
            .attr("x", 7)
            .attr("y", -margin.top / 2)
            .text(">1");

        //Draw Circles
        var circles = g.append("g")
            .attr("class", "circles");

        circles.selectAll("circle")
            .data(data)
            .enter()
            .append("circle")
            .attr("class", "circle")
            .style("fill", color)
            .attr("cx", function (d) {
                return x(d.unters_beginn);
            })
            .attr("cy", function (d) {
                return checkCircleValue(d[value], margin, y);
            })
            .attr("r", 4)
            .on("mouseover", function (d) {
                d3.select(this)
                    .attr("r", 7)
                    .style("fill", "lightslategray");

                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html(d.untart_name + "<br/>" + "Date: " +
                    formatTime(d.unters_beginn) + "<br/>" +
                    classNames[3] + ": " + d[value])
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY - 40) + "px");
            })
            .on("mouseout", function (d) {
                d3.select(this)
                    .attr("r", 4)
                    .style("fill", color);
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .on("click", function (d) {
                console.log("on Diff-Viewer Page: " + d.befund_schluessel);
                window.location = 'diff/' + d.befund_schluessel;
            });

        //Histogram
        var yBins = d3.histogram()
            .domain(y.domain())
            .thresholds(d3.range(y.domain()[0], y.domain()[1], (y.domain()[1]) / 5))
            .value(function (d) {
                if (d[value] > maxIntervalValue) {
                    return maxIntervalValue;
                } else {
                    return d[value];
                }
            })(data);

        yx.domain([0, d3.max(yBins, function (d) {
            return d.length;
        })]);

        var bWidth = y(yBins[0].x0) - y(yBins[0].x1) - 1;

        var yBar = gLeft.selectAll(".rect")
            .data(yBins)
            .enter()
            .append("rect")
            .attr("class", classNames[0])
            .attr("transform", function (d) {
                return "translate(" + 0 + "," + y(d.x1) + ")";
            })
            .attr("y", 1)
            .attr("class", classNames[0])
            .attr("width", function (d) {
                return yx(d.length);
            })
            .attr("height", bWidth)
            .on("mouseover", function (data) {
                g.selectAll("circle")
                    .filter(function (d) {
                        if (data.x0 > minIntervalValue && data.x1 === maxIntervalValue) {
                            return d[value] > data.x0;
                        }
                        else {
                            return d[value] >= data.x0 && d[value] <= data.x1;
                        }
                    })
                    .attr("r", 7)
                    .style("fill", "#666967");
                div.transition()
                    .duration(200)
                    .style("opacity", 1);
                div.html(function () {
                    if (counter < 2) {
                        return "Click to expand this interval"
                    }
                    else {
                        return "Click to reset interval"
                    }
                })
                    .style("left", (d3.event.pageX) + "px")
                    .style("top", (d3.event.pageY) + "px");
            })
            .on("mouseout", function () {
                g.selectAll("circle")
                    .data(data)
                    .attr("r", 4)
                    .style("fill", color);
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            })
            .on("click", function (d) {
                if (counter < 2) {
                    counter++;
                    var tempData = [];
                    minIntervalValue = Math.round(d.x0 * 10) / 10;
                    maxIntervalValue = Math.round(d.x1 * 10) / 10;

                    //Filter Interval Data
                    data.forEach(function (data) {
                        data[value] = +data[value];
                        data.unters_beginn = new Date(data.unters_beginn);
                        if (minIntervalValue === 0) {
                            if (data[value] >= minIntervalValue && data[value] <= maxIntervalValue) {
                                tempData.push(data);
                            }
                        } else {
                            if (data[value] > minIntervalValue && data[value] <= maxIntervalValue) {
                                tempData.push(data)
                            }
                        }
                    });

                    data = tempData;
                    redrawGraph(data, svg, height, width, gap, margin, y, yx, x, value, minIntervalValue, maxIntervalValue, classNames[0]);
                }
                else {
                    resetContent();
                }
                g.selectAll("circle")
                    .attr("r", 4)
                    .style("fill", color);
                div.transition()
                    .duration(500)
                    .style("opacity", 0);
            });

        gLeft.selectAll("text")
            .data(yBins)
            .enter()
            .append("text")
            .attr("class", "graphBar")
            .attr("x", function (d) {
                return yx(d.length) - 10;
            })
            .attr("transform", function (d) {
                return "translate(" + 0 + "," + (y(d.x1) + (bWidth / 2) + 5) + ")";
            })
            .text(function (data) {
                return data.length;
            });

        //Draw Median Line single
        g.append("line")
            .attr("class", "medianLineSingle")
            .style("stroke", color)
            .attr("x1", 0)
            .attr("y1", checkGraphArea(y(median_single[value]), height))
            .attr("x2", width)
            .attr("y2", checkGraphArea(y(median_single[value]), height));

        //Draw Median Line overall
        g.append("line")
            .attr("class", "medianLineAll")
            .attr("x1", 0)
            .attr("y1", checkGraphArea(y(median_all[value]), height))
            .attr("x2", width)
            .attr("y2", checkGraphArea(y(median_all[value]), height));

        //Draw Axes
        g.append("g")
            .attr("class", "x")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(x));

        brushArea.append("g")
            .attr("class", "x2")
            .call(d3.axisBottom(x2));

        g.append("g")
            .attr("class", "y")
            .call(d3.axisLeft(y)
                .ticks(6));

        g.append("g")
            .attr("class", "yx")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(yx)
                .ticks(4));

        //Append Brush
        brushArea.append("g")
            .attr("class", "brushTool")
            .call(brush)
            .call(brush.move, x.range());

        brushArea.selectAll("rect.handle")
            .attr("fill", color);

        //add Annotation of Axes
        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform", "rotate(-90)")
            .attr("y", 0 - margin.left - 3)
            .attr("x", 0 - (height / 2))
            .attr("dy", "1em")
            .text(classNames[3]);

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 12) + " ," +
                (height + margin.top - 10) + ")")
            .text("#Reports");

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 1.7) + " ," +
                (height + margin.top - 10) + ")")
            .text("Date");

        //add legend
        var legend = svg.append("g")
                .attr("class", "legend"),
            legendHeight = 8,
            legendLineLength = 20,
            legendGap = 80;

        legend.append("line")
            .attr("class", "medianLineSingle")
            .style("stroke", color)
            .attr("x1", width / 3)
            .attr("x2", width / 3 + legendLineLength)
            .attr("y1", legendHeight)
            .attr("y2", legendHeight);

        legend.append("line")
            .attr("class", "medianLineAll")
            .attr("x1", width / 2)
            .attr("x2", width / 2 + legendLineLength)
            .attr("y1", legendHeight)
            .attr("y2", legendHeight);

        legend.append("text")
            .attr("x", (width / 3) + legendLineLength + legendGap + 5)
            .attr("y", legendHeight)
            .attr("dy", "0.32em")
            .text("personal Median");

        legend.append("text")
            .attr("x", (width / 2) + legendLineLength + legendGap)
            .attr("y", legendHeight)
            .attr("dy", "0.32em")
            .text("overall Median");

        //Add Report Button
        var reportButton = svg.append("g")
                .attr("class", "reportButton"),
            buttonWidth = 150,
            buttonHeight = 20,
            x0 = width - 100,
            y0 = -0;

        reportButton.append("rect")
            .attr("class", classNames[1])
            .attr("width", buttonWidth)
            .attr("height", buttonHeight)
            .attr("x", function (d, i) {
                return x0 + (buttonWidth) * i;
            })
            .attr("y", y0)
            .attr("rx", 5)
            .attr("ry", 5);

        reportButton.append("text")
            .attr("class", classNames[2])
            .attr("x", function (d, i) {
                return x0 + buttonWidth * i + buttonWidth / 2;
            })
            .attr("y", y0 + buttonHeight / 2)
            .text("schreiben -> final");

        reportButton.on("click", function () {
            if (counter === 0) {
                var tempValue = value.slice(0, -3),
                    checkValue = value.substr(value.length - 3);

                if (checkValue === "s_f") {
                    value = tempValue + "g_f";
                    d3.selectAll("." + classNames[2]).text("gegenlesen -> final");
                }
                else {
                    value = tempValue + "s_f";
                    d3.selectAll("." + classNames[2]).text("schreiben -> final");
                }

                redrawGraph(data, svg, height, width, gap, margin, y, yx, x, value, minIntervalValue, maxIntervalValue, classNames[0]);

                if (tempValue === "jaccard_") {
                    redrawPieChart(d3.select("#SimilarityPieChartSingle"), median_single[value], ".pieChartFontSingle", specificValue, pieSegments);
                    redrawPieChart(d3.select("#SimilarityPieChartAll"), median_all[value], ".pieChartFontAll", specificValue, pieSegments)
                }
                else {
                    if (tempValue === "words_added_relative_") {
                        redrawBarChart(d3.select("#WordsAddedBarChart"), value, specificValue);
                    }
                    else {
                        redrawBarChart(d3.select("#WordsDeletedBarChart"), value, specificValue);
                    }
                }
            }
        });

        //Add Reset Button
        var resetButton = svg.append("g")
            .attr("class", "resetButton");
        x0 = width - 260;

        resetButton.append("rect")
            .attr("class", "buttonReset")
            .attr("width", buttonWidth)
            .attr("height", buttonHeight)
            .attr("x", function (d, i) {
                return x0 + (buttonWidth) * i;
            })
            .attr("y", y0)
            .attr("rx", 5)
            .attr("ry", 5);

        resetButton.append("text")
            .attr("class", "buttonAnnotationReset")
            .attr("x", function (d, i) {
                return x0 + buttonWidth * i + buttonWidth / 2;
            })
            .attr("y", y0 + buttonHeight / 2)
            .text("reset");

        resetButton.on("click", function () {
            resetContent();
        });

        //Brush function
        function brushed() {
            x.domain(d3.event.selection.map(x2.invert, x2));
            g.selectAll("circle")
                .attr("cx", function (d) {
                    if (x(d.unters_beginn) < gap + margin.right) {
                        return -100;
                    }
                    else {
                        return x(d.unters_beginn);
                    }
                });
            g.select(".x").call(d3.axisBottom(x));
        }
    }

    function drawPieChart(svg, medianValue, className, radius, pieSegments) {
        var margin = {top: 20, right: 55, bottom: 50, left: 45},
            width = +svg.attr("width"),
            height = +svg.attr("height");

        pieSegments[0].value = medianValue;
        pieSegments[1].value = 1.0 - medianValue;

        var arc = d3.arc()
            .outerRadius(radius - 10)
            .innerRadius(100);

        var pie = d3.pie()
            .sort(null)
            .value(function (d) {
                return d.value;
            });

        var g = svg.selectAll(".arc")
            .data(pie(pieSegments))
            .enter()
            .append("g")
            .attr("class", "arc")
            .attr("transform", "translate(" + width / 2 +
                "," + height / 2 + ")");

        g.append("path")
            .attr("d", arc)
            .style("fill", function (d) {
                return d.data.color;
            });

        g.append("text")
            .attr("class", className)
            .attr("text-anchor", "middle")
            .attr('y', 20)
            .text(medianValue.toPrecision(2));

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 10 - margin.right) + " ," +
                (height / 3 + margin.bottom) + ")")
            .text(function () {
                if (className === "pieChartFontSingle") {
                    return "personal Median"
                }
                else {
                    return "overall Median"
                }
            });
    }

    function drawBarChart(svg, value, color, maxValue) {
        var margin = {top: 50, right: 250, bottom: 50, left: 250},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var data = [{"name": "personal Median", "value": median_single[value].toPrecision(2), "color": color},
            {"name": "overall Median", "value": median_all[value].toPrecision(2), "color": "#666967"}];

        var x = d3.scaleLinear()
            .domain([0, maxValue])
            .range([0, width]);

        var y = d3.scaleBand()
            .domain(data.map(function (d) {
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
            .data(data)
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

    function redrawGraph(data, svg, height, width, gap, margin, y, yx, x, value, minIntervalValue, maxIntervalValue, className) {
        data.forEach(function (data) {
            data[value] = +data[value];
            data.unters_beginn = new Date(data.unters_beginn);
        });

        var intervalDivisor = 5;

        if ((Math.abs(maxIntervalValue - minIntervalValue)) <= 0.3) {
            intervalDivisor = 2;
        }

        //Redefine y-Axis
        y.domain([minIntervalValue, maxIntervalValue]);

        //Redraw y-Axis
        svg.selectAll(".y")
            .transition()
            .call(d3.axisLeft(y)
                .ticks(intervalDivisor));

        //Redraw Gridlines
        svg.selectAll(".grid").transition()
            .call(d3.axisLeft(y)
                .ticks(intervalDivisor)
                .tickSize(-width)
                .tickFormat(""));

        //Redraw Circles
        var circles = svg.selectAll("circle")
            .data(data);

        circles.exit().remove();

        circles.enter().append("circle");

        circles.transition()
            .attr("cx", function (d) {
                if (x(d.unters_beginn) < gap + margin.right) {
                    return -100;
                }
                else {
                    return x(d.unters_beginn);
                }
            })
            .attr("cy", function (d) {
                return checkCircleValue(d[value], margin, y);
            });

        //Redraw Histogram
        var yBins = d3.histogram()
            .domain(y.domain())
            .thresholds(d3.range(y.domain()[0], y.domain()[1], (y.domain()[1] - y.domain()[0]) / intervalDivisor))
            .value(function (d) {
                if (d[value] > maxIntervalValue) {
                    return maxIntervalValue;
                } else {
                    return d[value];
                }
            })(data);

        yx.domain([0, d3.max(yBins, function (d) {
            return d.length;
        })]);

        svg.selectAll(".yx")
            .transition()
            .call(d3.axisBottom(yx)
                .ticks(4));

        var bWidth = y(yBins[0].x0) - y(yBins[0].x1) - 1;

        var bars = svg.selectAll("rect." + className)
            .data(yBins);

        bars.exit().remove();

        bars.enter().append("rect");

        bars.transition()
            .attr("width", function (d) {
                return yx(d.length);
            })
            .attr("height", bWidth)
            .attr("transform", function (d) {
                return "translate(" + 0 + "," + y(d.x1) + ")";
            });

        //Redraw BarText
        var barText = svg.selectAll("text.graphBar")
            .data(yBins);

        barText.exit().remove();

        barText.enter().append("text");

        barText.transition()
            .attr("x", function (d) {
                return yx(d.length) - 10;
            })
            .attr("transform", function (d) {
                return "translate(" + 0 + "," + (y(d.x1) + (bWidth / 2) + 5) + ")";
            })
            .text(function (data) {
                return data.length;
            });

        //Redraw Median Lines
        svg.select(".medianLineSingle").transition()
            .attr("y1", checkGraphArea(y(median_single[value]), height))
            .attr("y2", checkGraphArea(y(median_single[value]), height));

        svg.select(".medianLineAll").transition()
            .attr("y1", checkGraphArea(y(median_all[value]), height))
            .attr("y2", checkGraphArea(y(median_all[value]), height));
    }

    function redrawBarChart(svg, words, maxValue) {
        var margin = {top: 50, right: 250, bottom: 50, left: 250},
            width = +svg.attr("width") - margin.left - margin.right;

        var data = [median_single[words].toPrecision(2), median_all[words].toPrecision(2)];

        var x = d3.scaleLinear()
            .domain([0, maxValue])
            .range([0, width]);

        svg.selectAll("rect.bar")
            .data(data)
            .transition()
            .attr("width", function (d) {
                if (d > maxValue) {
                    return x(maxValue)
                } else {
                    return x(d)
                }
            });

        svg.selectAll("text.barText")
            .data(data)
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

    function redrawPieChart(svg, value, className, radius, pieSegments) {
        pieSegments[0].value = value;
        pieSegments[1].value = 1 - value;

        var arc = d3.arc()
            .outerRadius(radius - 10)
            .innerRadius(100);

        var pie = d3.pie()
            .sort(null)
            .value(function (d) {
                return d.value;
            });

        svg.selectAll(".arc").select("path")
            .data(pie(pieSegments))
            .attr("d", arc);

        svg.selectAll(className).transition()
            .text(pieSegments[0].value.toPrecision(2));
    }

    function resetContent() {
        counter = 0;
        d3.selectAll("svg").selectAll("g").remove();
        d3.selectAll(".tooltip").remove();
        d3.csv(data_url(), function (error, data) {
            if (error) throw error;
            drawSimilarityGraph(data);
            drawWordsAddedGraph(data);
            drawWordsDeletedGraph(data);
        });
    }

    function checkGraphArea(value, height) {
        if (value < 0 || value > height) {
            return -100;
        }
        else {
            return value;
        }
    }

    function checkCircleValue(value, margin, y) {
        if (value > 1) {
            return -margin.top / 3
        }
        else {
            return y(value);
        }
    }

    function checkboxHandler() {
        var checkboxValues = JSON.parse(localStorage.getItem('departments')) || {};
        $.each(checkboxValues, function (key, value) {
            $("#" + key).prop('checked', value);
        });

        var checkboxes = $('#checkboxes :checkbox');

        checkboxes.on('change', function () {
            var departments = [];
            checkboxes.each(function () {
                checkboxValues[this.id] = this.checked;
                if (this.checked) {
                    departments.push(this.id);
                    this.value = this.id;
                }
                else {
                    this.value = null
                }
            });
            localStorage.setItem('departments', JSON.stringify(checkboxValues));
            $('#departments').val(departments);
        });
    }
});