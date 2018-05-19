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
        d3.csv(data_url(), function (data) {
            draw_hist(data);
        });

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

    function draw_hist(data) {
        // Assign the specification to a local variable vlSpec.
        var vlSpec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
            "data": {"values": data, "format": "csv"},
            "mark": "bar",
            "encoding": {
                "y": {
                    "bin": {"step": 0.2},
                    "field": "jaccard_s_f",
                    "type": "quantitative",
                    "axis": {
                        "title": "S->F similarity"
                    }
                },
                "x": {
                    "aggregate": "count", "type": "quantitative",
                    "axis": {
                        "title": "#Reports"
                    }
                },
                "color": {"value": "#6b486b"}
            }
        };
        // Embed the visualization in the container with id `vis`
        vegaEmbed("#vis_s_f", vlSpec, {"actions": false});
    }


    function draw_SimilarityGraph() {
        var svg = d3.select("#grouped"),
            margin = {top: 20, right: 20, bottom: 20, left: 40},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            gap = 170;
        g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

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
                .attr("r", 4);

            var yBins = d3.histogram()
                .domain(y.domain())
                .thresholds(d3.range(0,  y.domain()[1], (y.domain()[1])/5))
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

            console.log(yBins);

            var bWidth = y(yBins[0].x0) - y(yBins[0].x1) - 1;

            yBar.append("rect")
                .attr("y", 1)
                .attr("class", "bar")
                .attr("width", function (d) {
                    return yx(d.length);
                })
                .attr("height", bWidth);

            yBar.append("text")
                .attr("dx", "-.75em")
                .attr("y", bWidth / 2 + 1)
                .attr("x", function (d) {
                    return yx(d.length);
                })
                .attr("text-anchor", "middle")
                .text(function (d) {
                    return d.length
                })
                .style("fill", "white")
                .style("font", "9px sans-serif");


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
        });
    }

    function draw_add_delete() {
        var svg = d3.select("#add_delete"),
            margin = {top: 20, right: 20, bottom: 30, left: 40},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var x0 = d3.scaleBand()
            .rangeRound([0, width])
            .paddingInner(0.1);

        var x1 = d3.scaleBand()
            .padding(0.05);

        var y = d3.scaleLinear()
            .rangeRound([height, 0]);

        var z = d3.scaleOrdinal()
            .range(["#2CA02C", "#d62728"]);

        d3.csv(data_url(), function (d, i, columns) {
            for (i = 1, n = columns.length; i < n; ++i) {
                if (columns[i] === 'unters_beginn') {
                    d[columns[i]] = new Date(d[columns[i]]);
                } else {
                    var number = +d[columns[i]];
                    d[columns[i]] = isNaN(+d[columns[i]]) ? d[columns[i]] : +d[columns[i]];
                }
            }
            return d;
        }, function (error, data) {
            if (error) throw error;
            var keys = ['words_added_g_f_relative', 'words_deleted_g_f_relative'];
            x0.domain(data.map(function (d) {
                return d.unters_beginn;
            }));
            x1.domain(keys).rangeRound([0, x0.bandwidth()]);
            y.domain([0, d3.max(data, function (d) {
                return d3.max(keys, function (key) {
                    return d[key];
                });
            })]).nice();

            g.append("g")
                .selectAll("g")
                .data(data)
                .enter().append("g")
                .attr("transform", function (d) {
                    return "translate(" + x0(d.unters_beginn) + ",0)";
                })
                .selectAll("rect")
                .data(function (d) {
                    return keys.map(function (key) {
                        return {key: key, value: d[key]};
                    });
                })
                .enter().append("rect")
                .attr("x", function (d) {
                    return x1(d.key);
                })
                .attr("y", function (d) {
                    return y(d.value);
                })
                .attr("width", x1.bandwidth())
                .attr("height", function (d) {
                    return height - y(d.value);
                })
                .attr("fill", function (d) {
                    return z(d.key);
                });

            g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x0).tickFormat(d3.timeFormat('%d.%m')));

            g.append("g")
                .attr("class", "axis")
                .call(d3.axisLeft(y).ticks(8, ".0%"))
                .append("text")
                .attr("x", 5)
                .attr("y", y(y.ticks().pop()) + 0.5)
                .attr("dy", "0.32em")
                .attr("fill", "#000")
                .attr("font-weight", "bold")
                .attr("text-anchor", "start")
                .text("Relative additions/deletions of words");

            var legend = g.append("g")
                .attr("font-family", "sans-serif")
                .attr("font-size", 10)
                .attr("text-anchor", "end")
                .selectAll("g")
                .data(keys.slice().reverse())
                .enter().append("g")
                .attr("transform", function (d, i) {
                    return "translate(0," + i * 20 + ")";
                });

            legend.append("rect")
                .attr("x", width - 19)
                .attr("width", 19)
                .attr("height", 19)
                .attr("fill", z);

            legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9.5)
                .attr("dy", "0.32em")
                .text(function (d) {
                    if (d === 'words_added_g_f_relative') {
                        return 'Words added after Gegengelesen (relativ)';
                    } else if (d === 'words_deleted_g_f_relative') {
                        return 'Words deleted after Gegengelesen (relativ)'
                    }
                });
        });
    }

    function draw_add_delete_absolute() {
        var svg = d3.select("#add_delete_absolute"),
            margin = {top: 20, right: 20, bottom: 30, left: 40},
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

        var x0 = d3.scaleBand()
            .rangeRound([0, width])
            .paddingInner(0.1);

        var x1 = d3.scaleBand()
            .padding(0.05);

        var y = d3.scaleLinear()
            .rangeRound([height, 0]);

        var z = d3.scaleOrdinal()
            .range(["#2CA02C", "#d62728"]);

        d3.csv(data_url(), function (d, i, columns) {
            for (var i = 1, n = columns.length; i < n; ++i) {
                if (columns[i] === 'unters_beginn') {
                    d[columns[i]] = new Date(d[columns[i]]);
                } else {
                    var number = +d[columns[i]];
                    d[columns[i]] = isNaN(+d[columns[i]]) ? d[columns[i]] : +d[columns[i]];
                }
            }
            return d;
        }, function (error, data) {
            if (error) throw error;
            var keys = ['words_added_g_f', 'words_deleted_g_f']
            x0.domain(data.map(function (d) {
                return d.unters_beginn;
            }));
            x1.domain(keys).rangeRound([0, x0.bandwidth()]);
            y.domain([0, d3.max(data, function (d) {
                return d3.max(keys, function (key) {
                    return d[key];
                });
            })]).nice();

            g.append("g")
                .selectAll("g")
                .data(data)
                .enter().append("g")
                .attr("transform", function (d) {
                    return "translate(" + x0(d.unters_beginn) + ",0)";
                })
                .selectAll("rect")
                .data(function (d) {
                    return keys.map(function (key) {
                        return {key: key, value: d[key]};
                    });
                })
                .enter().append("rect")
                .attr("x", function (d) {
                    return x1(d.key);
                })
                .attr("y", function (d) {
                    return y(d.value);
                })
                .attr("width", x1.bandwidth())
                .attr("height", function (d) {
                    return height - y(d.value);
                })
                .attr("fill", function (d) {
                    return z(d.key);
                });

            g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x0).tickFormat(d3.timeFormat('%d.%m')));

            g.append("g")
                .attr("class", "axis")
                .call(d3.axisLeft(y).ticks(8))
                .append("text")
                .attr("x", 5)
                .attr("y", y(y.ticks().pop()) + 0.5)
                .attr("dy", "0.32em")
                .attr("fill", "#000")
                .attr("font-weight", "bold")
                .attr("text-anchor", "start")
                .text("Absolute additions/deletions of words");

            var legend = g.append("g")
                .attr("font-family", "sans-serif")
                .attr("font-size", 10)
                .attr("text-anchor", "end")
                .selectAll("g")
                .data(keys.slice().reverse())
                .enter().append("g")
                .attr("transform", function (d, i) {
                    return "translate(0," + i * 20 + ")";
                });

            legend.append("rect")
                .attr("x", width - 19)
                .attr("width", 19)
                .attr("height", 19)
                .attr("fill", z);

            legend.append("text")
                .attr("x", width - 24)
                .attr("y", 9.5)
                .attr("dy", "0.32em")
                .text(function (d) {
                    if (d === 'words_added_g_f') {
                        return 'Words added after Gegengelesen (absolute)';
                    } else if (d === 'words_deleted_g_f') {
                        return 'Words deleted after Gegengelesen (absolute)'
                    }
                });
        });
    }

});