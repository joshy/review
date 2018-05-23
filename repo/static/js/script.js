$(function () {

    var picker = new Pikaday({
        field: document.getElementById('datepicker'),
        format: 'DD.MM.YYYY'
    });

    var startDatePicker = $('#start_date').pikaday({
        format: 'DD.MM.YYYY',
        firstDay: 1,
        minDate: new Date(2017, 10, 1),
        maxDate: new Date(),
        yearRange: [2017, 2018]
    });

    var endDatePicker = $('#end_date').pikaday({
        format: 'DD.MM.YYYY',
        firstDay: 1,
        minDate: new Date(2017, 10, 1),
        maxDate: new Date(),
        yearRange: [2017, 2018]
    });

    if ('diff' == $('body').data('page')) {
        diff();
    }

    function diff() {
        var writing = $('#writing').text();
        var final = $('#final').text();
        var diff = JsDiff.diffWords(writing, final);
        var display = $('#diff').get(0);
        while (display.firstChild) {
            display.removeChild(display.firstChild);
        }
        var fragment = document.createDocumentFragment();

        diff.forEach(function (part) {
            // green for additions, red for deletions
            // grey for common parts
            color = part.added ? 'green' :
                part.removed ? 'red' : 'grey';
            span = document.createElement('span');
            span.style.color = color;
            if (part.removed === true) {
                span.className = "strike";
            }
            span.appendChild(document.createTextNode(part.value));
            fragment.appendChild(span);
        });
        display.appendChild(fragment);
    }

    $('input[type=radio][name=befund_text]').change(function () {
        var writing = $('#writing');
        var x = document.getElementById(this.value).textContent;
        writing.text(x);
        diff();
        if (this.value === 'befund_s') {
            $('#words_added_g_f').addClass('dn');
            $('#words_deleted_g_f').addClass('dn');
            $('#jaccard_g_f').addClass('dn');
            $('#words_added_s_f').removeClass('dn');
            $('#words_deleted_s_f').removeClass('dn');
            $('#jaccard_s_f').removeClass('dn')
        } else if (this.value === 'befund_g') {
            $('#words_added_g_f').removeClass('dn');
            $('#words_deleted_g_f').removeClass('dn');
            $('#jaccard_g_f').removeClass('dn');
            $('#words_added_s_f').addClass('dn');
            $('#words_deleted_s_f').addClass('dn');
            $('#jaccard_s_f').addClass('dn')
        }
    });

    if ('dashboard' == $('body').data('page')) {
        console.log('on dashboard page');
        drawSimilarityGraph();
        drawSimilarityDoughnutSingle();
        drawSimilarityDoughnutAll();
        /*drawWordsAddedGraph();*/
        drawDoughnutWordsAddedSingle();
        drawDoughnutWordsAddedAll();
    }

    function data_url() {
        var writer = document.getElementById('writer').value;
        var last_exams = document.getElementById('last_exams').value;
        var start_date = document.getElementById('start_date').value;
        var end_date = document.getElementById('end_date').value;
        param = {
            'w': writer,
            'last_exams': last_exams,
            'start_date': start_date,
            'end_date': end_date
        };
        return 'dashboard/data?' + $.param(param)
    }

    function drawSimilarityGraph() {
        var svg = d3.select("#SimilarityGraph"),
            margin = {top: 20, right: 20, bottom: 40, left: 45},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            gap = 170;
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var formatTime = d3.timeFormat("%d.%m.%Y");

        //Define Axes
        var x = d3.scaleTime().range([gap + 20, width]),
            y = d3.scaleLinear().range([height, 0]).domain([0, 1]),
            yx = d3.scaleLinear().range([0, gap]);

        //Define Gridlines
        function make_yAxis_gridlines() {
            return d3.axisLeft(y)
                .ticks(4)
        }

        function make_xAxis_gridlines() {
            return d3.axisBottom(yx)
                .ticks(3)
        }

        //Draw Gridlines
        g.append("g")
            .attr("class", "grid")
            .call(make_yAxis_gridlines()
                .tickSize(-width)
                .tickFormat("")
            );

        //Define Histogramm
        var gLeft = svg.append("g")
            .attr("transform",
                "translate(" + (margin.left) + "," + margin.top + ")");

        // Define the div for the tooltip
        var div = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        //Get Data
        d3.csv(data_url(), function (error, data) {
            if (error) throw error;
            data.forEach(function (data) {
                data.jaccard_s_f = +data.jaccard_s_f;
                data.unters_beginn = new Date(data.unters_beginn);
            });

            x.domain(d3.extent(data, function (d) {
                return d.unters_beginn;
            }));

            //Draw Circles
            g.selectAll("circle")
                .data(data)
                .enter()
                .append("circle")
                .attr("class", "circle")
                .attr("cx", function (d) {
                    return x(d.unters_beginn);
                })
                .attr("cy", function (d) {
                    return y(d.jaccard_s_f);
                })
                .attr("r", 4)
                .on("mouseover", function (d) {
                    d3.select(this)
                        .attr("r", 7)
                        .style("fill", "red");

                    div.transition()
                        .duration(200)
                        .style("opacity", 1);
                    div.html(d.untart_name + "<br/>" + "Date: " +
                        formatTime(d.unters_beginn) + "<br/>" +
                        "Similarity: " + d.jaccard_s_f)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 40) + "px");
                })
                .on("mouseout", function (d) {
                    d3.select(this)
                        .attr("r", 4)
                        .style("fill", "steelblue");
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
                    return d.jaccard_s_f;
                })(data);

            yx.domain([0, d3.max(yBins, function (d) {
                return d.length;
            })]);

            g.append("g")
                .attr("class", "grid")
                .attr("transform", "translate(0," + height + ")")
                .call(make_xAxis_gridlines()
                    .tickFormat("")
                );

            var yBar = gLeft.selectAll(".bar")
                .data(yBins)
                .enter()
                .append("g")
                .attr("class", "bar")
                .attr("transform", function (d) {
                    return "translate(" + 0 + "," + y(d.x1) + ")";
                });

            var bWidth = y(yBins[0].x0) - y(yBins[0].x1) - 1;

            yBar.append("rect")
                .attr("y", 1)
                .attr("class", "bar")
                .attr("width", function (d) {
                    return yx(d.length);
                })
                .attr("height", bWidth)
                .on("mouseover", function (data) {
                    g.selectAll("circle")
                        .filter(function (d) {
                            return d.jaccard_s_f >= data.x0 && d.jaccard_s_f <= data.x1;
                        })
                        .attr("r", 7)
                        .style("fill", "red");
                    div.transition()
                        .duration(200)
                        .style("opacity", 1);
                    div.html(data.length)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY) + "px");
                })
                .on("mouseout", function () {
                    g.selectAll("circle")
                        .data(data)
                        .attr("r", 4)
                        .style("fill", "steelblue");
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
                });

            var medianValueSingle = median_single["jaccard_s_f"];
            var medianValueAll = median_all["jaccard_s_f"];

            //Draw Median Line single
            g.append("line")
                .attr("class", "medianLineSingle")
                .attr("x1", 0)
                .attr("y1", y(medianValueSingle))
                .attr("x2", width)
                .attr("y2", y(medianValueSingle));

            //Draw Median Line overall
            g.append("line")
                .attr("class", "medianLineAll")
                .attr("x1", 0)
                .attr("y1", y(medianValueAll))
                .attr("x2", width)
                .attr("y2", y(medianValueAll));

            //Draw Axes
            g.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x));

            g.append("g")
                .call(d3.axisLeft(y)
                    .ticks(6));

            g.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(yx)
                    .ticks(3));
            //add Annotation of Axes
            g.append("text")
                .attr("class", "axisAnnotation")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left - 3)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .text("Similarity");

            g.append("text")
                .attr("class", "axisAnnotation")
                .attr("transform",
                    "translate(" + (width / 12) + " ," +
                    (height + margin.top + 12) + ")")
                .text("#Reports");

            g.append("text")
                .attr("class", "axisAnnotation")
                .attr("transform",
                    "translate(" + (width / 1.7) + " ," +
                    (height + margin.top + 12) + ")")
                .text("Date");

            //add legend
            var legend = svg.append("g")
                .attr("class", "legend");

            legend.append("line")
                .attr("class", "medianLineSingle")
                .attr("x1", width / 2)
                .attr("x2", width / 2 + 20)
                .attr("y1", 5)
                .attr("y2", 5);

            legend.append("line")
                .attr("class", "medianLineAll")
                .attr("x1", width / 1.6)
                .attr("x2", width / 1.6 + 20)
                .attr("y1", 5)
                .attr("y2", 5);

            legend.append("text")
                .attr("x", width / 2 + 100)
                .attr("y", 5)
                .attr("dy", "0.32em")
                .text("personal Median");

            legend.append("text")
                .attr("x", width / 1.6 + 95)
                .attr("y", 5)
                .attr("dy", "0.32em")
                .text("overall Median")
        });
    }

    function drawSimilarityDoughnutSingle() {
        var svg = d3.select("#SimilarityDoughnutSingle"),
            margin = {top: 20, right: 55, bottom: 50, left: 45},
            width = +svg.attr("width"),
            height = +svg.attr("height"),
            radius = 150;

        var pieSegments = [
            {name: 'medianValue', value: 0.0, color: 'steelblue'},
            {name: 'maxValue', value: 0.0, color: 'lightgrey'},
        ];

        var medianValueSingle = median_single["jaccard_s_f"];

        pieSegments[0].value = medianValueSingle;
        pieSegments[1].value = 1.0 - medianValueSingle;

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
            .attr("transform", "translate(" + width / 2 +
                "," + height / 2 + ")");

        g.append("path")
            .attr("d", arc)
            .style("fill", function (d) {
                return d.data.color;
            });

        g.append("text")
            .attr("class", "doughnutFontSingle")
            .attr("text-anchor", "middle")
            .attr('y', 20)
            .text(medianValueSingle.toPrecision(2));

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 10 - margin.right) + " ," +
                (height / 3 + margin.bottom) + ")")
            .text("personal Median");
    }

    function drawSimilarityDoughnutAll() {
        var svg = d3.select("#SimilarityDoughnutAll"),
            margin = {top: 20, right: 55, bottom: 50, left: 45},
            width = +svg.attr("width"),
            height = +svg.attr("height"),
            radius = 150;

        var pieSegments = [
            {name: 'medianValue', value: 0.0, color: 'red'},
            {name: 'maxValue', value: 0.0, color: 'lightgrey'},
        ];

        var medianValueAll = median_all["jaccard_s_f"];

        pieSegments[0].value = medianValueAll;
        pieSegments[1].value = 1.0 - medianValueAll;

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
            .attr("transform", "translate(" + width / 2 +
                "," + height / 2 + ")");

        g.append("path")
            .attr("d", arc)
            .style("fill", function (d) {
                return d.data.color;
            });

        g.append("text")
            .attr("class", "doughnutFontAll")
            .attr("text-anchor", "middle")
            .attr('y', 20)
            .text(medianValueAll.toPrecision(2));

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 10 - margin.right) + " ," +
                (height / 3 + margin.bottom) + ")")
            .text("overall Median");
    }

    function drawWordsAddedGraph() {
        var svg = d3.select("#WordsAddedGraph"),
            margin = {top: 20, right: 20, bottom: 40, left: 45},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            gap = 170;
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var formatTime = d3.timeFormat("%d.%m.%Y");

        //Define Axes
        var x = d3.scaleTime().range([gap + 20, width]),
            y = d3.scaleLinear().range([height, 0]).domain([0, 50]),
            yx = d3.scaleLinear().range([0, gap]);

        //Define Gridlines
        function make_yAxis_gridlines() {
            return d3.axisLeft(y)
                .ticks(4)
        }

        function make_xAxis_gridlines() {
            return d3.axisBottom(yx)
                .ticks(3)
        }

        //Draw Gridlines
        g.append("g")
            .attr("class", "grid")
            .call(make_yAxis_gridlines()
                .tickSize(-width)
                .tickFormat("")
            );

        //Define Histogramm
        var gLeft = svg.append("g")
            .attr("transform",
                "translate(" + (margin.left) + "," + margin.top + ")");

        // Define the div for the tooltip
        var div = d3.select("body")
            .append("div")
            .attr("class", "tooltip")
            .style("opacity", 0);

        //Get Data
        d3.csv(data_url(), function (error, data) {
            if (error) throw error;
            data.forEach(function (data) {
                data.words_added_s_f = +data.words_added_s_f;
                data.unters_beginn = new Date(data.unters_beginn);
            });

            x.domain(d3.extent(data, function (d) {
                return d.unters_beginn;
            }));

            //Draw Circles
            g.selectAll("circle")
                .data(data)
                .enter()
                .append("circle")
                .attr("class", "circle")
                .attr("cx", function (d) {
                    return x(d.unters_beginn);
                })
                .attr("cy", function (d) {
                    return y(d.words_added_s_f);
                })
                .attr("r", 4)
                .on("mouseover", function (d) {
                    d3.select(this)
                        .attr("r", 7)
                        .style("fill", "red");

                    div.transition()
                        .duration(200)
                        .style("opacity", 1);
                    div.html(d.untart_name + "<br/>" + "Date: " +
                        formatTime(d.unters_beginn) + "<br/>" +
                        "Words added: " + d.words_added_s_f)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY - 40) + "px");
                })
                .on("mouseout", function (d) {
                    d3.select(this)
                        .attr("r", 4)
                        .style("fill", "steelblue");
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
                    return d.words_added_s_f;
                })(data);

            yx.domain([0, d3.max(yBins, function (d) {
                return d.length;
            })]);

            g.append("g")
                .attr("class", "grid")
                .attr("transform", "translate(0," + height + ")")
                .call(make_xAxis_gridlines()
                    .tickSize(-height)
                    .tickFormat("")
                );

            var yBar = gLeft.selectAll(".bar")
                .data(yBins)
                .enter()
                .append("g")
                .attr("class", "bar")
                .attr("transform", function (d) {
                    return "translate(" + 0 + "," + y(d.x1) + ")";
                });

            var bWidth = y(yBins[0].x0) - y(yBins[0].x1) - 1;

            yBar.append("rect")
                .attr("y", 1)
                .attr("class", "bar")
                .attr("width", function (d) {
                    return yx(d.length);
                })
                .attr("height", bWidth)
                .on("mouseover", function (data) {
                    g.selectAll("circle")
                        .filter(function (d) {
                            return d.words_added_s_f >= data.x0 && d.words_added_s_f <= data.x1;
                        })
                        .attr("r", 7)
                        .style("fill", "red");
                    div.transition()
                        .duration(200)
                        .style("opacity", 1);
                    div.html(data.length)
                        .style("left", (d3.event.pageX) + "px")
                        .style("top", (d3.event.pageY) + "px");
                })
                .on("mouseout", function () {
                    g.selectAll("circle")
                        .data(data)
                        .attr("r", 4)
                        .style("fill", "steelblue");
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
                });

            var medianValueSingle = median_single["jaccard_s_f"];
            var medianValueAll = median_all["jaccard_s_f"];

            //Draw Median Line single
            g.append("line")
                .attr("class", "medianLineSingle")
                .attr("x1", 0)
                .attr("y1", y(medianValueSingle))
                .attr("x2", width)
                .attr("y2", y(medianValueSingle));

            //Draw Median Line overall
            g.append("line")
                .attr("class", "medianLineAll")
                .attr("x1", 0)
                .attr("y1", y(medianValueAll))
                .attr("x2", width)
                .attr("y2", y(medianValueAll));

            //Draw Axes
            g.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x));

            g.append("g")
                .call(d3.axisLeft(y)
                    .ticks(6));

            g.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(yx)
                    .ticks(3));
            //add Annotation of Axes
            g.append("text")
                .attr("class", "axisAnnotation")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left - 3)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .text("Similarity");

            g.append("text")
                .attr("class", "axisAnnotation")
                .attr("transform",
                    "translate(" + (width / 12) + " ," +
                    (height + margin.top + 12) + ")")
                .text("#Reports");

            g.append("text")
                .attr("class", "axisAnnotation")
                .attr("transform",
                    "translate(" + (width / 1.7) + " ," +
                    (height + margin.top + 12) + ")")
                .text("Date");

            //add legend
            var legend = svg.append("g")
                .attr("class", "legend");

            legend.append("line")
                .attr("class", "medianLineSingle")
                .attr("x1", width / 2)
                .attr("x2", width / 2 + 20)
                .attr("y1", 5)
                .attr("y2", 5);

            legend.append("line")
                .attr("class", "medianLineAll")
                .attr("x1", width / 1.6)
                .attr("x2", width / 1.6 + 20)
                .attr("y1", 5)
                .attr("y2", 5);

            legend.append("text")
                .attr("x", width / 2 + 100)
                .attr("y", 5)
                .attr("dy", "0.32em")
                .text("personal Median");

            legend.append("text")
                .attr("x", width / 1.6 + 95)
                .attr("y", 5)
                .attr("dy", "0.32em")
                .text("overall Median")
        });
    }

    function drawDoughnutWordsAddedSingle() {
        var svg = d3.select("#WordsAddedDoughnutSingle"),
            margin = {top: 20, right: 55, bottom: 50, left: 45},
            width = +svg.attr("width"),
            height = +svg.attr("height"),
            radius = 150;

        var pieSegments = [
            {name: 'medianValue', value: 0.0, color: 'steelblue'},
            {name: 'maxValue', value: 0.0, color: 'lightgrey'},
        ];

        var medianValueSingle = median_single["words_added_s_f"];

        pieSegments[0].value = medianValueSingle;
        pieSegments[1].value = 1.0 - medianValueSingle;

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
            .attr("transform", "translate(" + width / 2 +
                "," + height / 2 + ")");

        g.append("path")
            .attr("d", arc)
            .style("fill", function (d) {
                return d.data.color;
            });

        g.append("text")
            .attr("class", "doughnutFontSingle")
            .attr("text-anchor", "middle")
            .attr('y', 20)
            .text(Math.round(medianValueSingle));

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 10 - margin.right) + " ," +
                (height / 3 + margin.bottom) + ")")
            .text("personal Median");
    }

    function drawDoughnutWordsAddedAll() {
        var svg = d3.select("#WordsAddedDoughnutAll"),
            margin = {top: 20, right: 55, bottom: 50, left: 45},
            width = +svg.attr("width"),
            height = +svg.attr("height"),
            radius = 150;

        var pieSegments = [
            {name: 'medianValue', value: 0.0, color: 'red'},
            {name: 'maxValue', value: 0.0, color: 'lightgrey'},
        ];

        var medianValueAll = median_all["words_added_s_f"];
        pieSegments[0].value = medianValueAll;
        pieSegments[1].value = 1.0 - medianValueAll;

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
            .attr("transform", "translate(" + width / 2 +
                "," + height / 2 + ")");

        g.append("path")
            .attr("d", arc)
            .style("fill", function (d) {
                return d.data.color;
            });

        g.append("text")
            .attr("class", "doughnutFontAll")
            .attr("text-anchor", "middle")
            .attr('y', 20)
            .text(Math.round(medianValueAll));

        g.append("text")
            .attr("class", "axisAnnotation")
            .attr("transform",
                "translate(" + (width / 10 - margin.right) + " ," +
                (height / 3 + margin.bottom) + ")")
            .text("overall Median");

    }

    /*function median(values) {

        if (values.length === 0) {
            return 0;
        }

        values.sort(function (a, b) {
            return a - b;
        });

        var half = Math.floor(values.length / 2);

        if (values.length % 2) {
            return values[half];
        }
        else {
            return (values[half - 1] + values[half]) / 2.0;
        }
    }*/
});