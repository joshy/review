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
        var writing = $('#writing')
        var x = document.getElementById(this.value).textContent
        writing.text(x)
        diff();
        if (this.value === 'befund_s') {
            $('#words_added_g_f').addClass('dn')
            $('#words_deleted_g_f').addClass('dn')
            $('#jaccard_g_f').addClass('dn')
            $('#words_added_s_f').removeClass('dn')
            $('#words_deleted_s_f').removeClass('dn')
            $('#jaccard_s_f').removeClass('dn')
        } else if (this.value === 'befund_g') {
            $('#words_added_g_f').removeClass('dn')
            $('#words_deleted_g_f').removeClass('dn')
            $('#jaccard_g_f').removeClass('dn')
            $('#words_added_s_f').addClass('dn')
            $('#words_deleted_s_f').addClass('dn')
            $('#jaccard_s_f').addClass('dn')
        }
    });

    if ('dashboard' == $('body').data('page')) {
        console.log('on dashboard page');
        draw_SimilarityGraph();
        draw_MedianDougnut();
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

    function draw_SimilarityGraph() {
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
        var div = d3.select("body").append("div")
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
                    .tickSize(-height)
                    .tickFormat("")
                );

            var yBar = gLeft.selectAll(".bar")
                .data(yBins)
                .enter().append("g")
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

            //Draw Axes
            g.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x));

            g.append("g")
                .call(d3.axisLeft(y)
                    .ticks(6));

            g.append("text")
                .attr("transform", "rotate(-90)")
                .attr("y", 0 - margin.left - 3)
                .attr("x", 0 - (height / 2))
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .style("font-size", "15px")
                .style("font-weight", "bold")
                .text("Similarity");

            g.append("text")
                .attr("transform",
                    "translate(" + (width / 12) + " ," +
                    (height + margin.top + 12) + ")")
                .style("text-anchor", "middle")
                .style("font-size", "15px")
                .style("font-weight", "bold")
                .text("#Reports");

            g.append("text")
                .attr("transform",
                    "translate(" + (width / 1.7) + " ," +
                    (height + margin.top + 12) + ")")
                .style("text-anchor", "middle")
                .style("font-size", "15px")
                .style("font-weight", "bold")
                .text("Date");


            g.append("g")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(yx)
                    .ticks(3));
        });
    }

    function draw_MedianDougnut() {

        var medianValue = 0.0;
        var pieSegments = [
            {name: 'maxValue', value: 0.0, color: 'lightgrey'},
            {name: 'medianValue', value: 0.0, color: 'steelblue'},
        ];

        d3.csv(data_url(), function (error, data) {
            if (error) throw error;
            var similarityList = data.map(function (d) {
                return parseFloat(d.jaccard_s_f);
            });
            medianValue = median(similarityList);
            pieSegments[0].value = 1.0 - medianValue;
            pieSegments[1].value = medianValue;
            console.log(pieSegments[1]);

            var width = 400,
                height = 400,
                radius = 150;

            var arc = d3.arc()
                .outerRadius(radius - 10)
                .innerRadius(100);

            var pie = d3.pie()
                .sort(null)
                .value(function(d) { return d.value; });

            var svg = d3.select("#MedianDoughnut")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

            var g = svg.selectAll(".arc")
                .data(pie(pieSegments))
                .enter()
                .append("g");

            g.append("path")
                .attr("d", arc)
                .style("fill", function (d, i) {
                    return d.data.color;
                });

            g.append("text")
                .attr("text-anchor", "middle")
                .attr('font-size', '4em')
                .attr('y', 20)
                .text(medianValue.toPrecision(1));

        });
    }

    function median(values) {

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
    }
});