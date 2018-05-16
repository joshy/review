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

    $('input[type=radio][name=befund_text]').change(function() {
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
        draw_grouped();
        draw_add_delete();
        draw_add_delete_absolute();
        d3.csv(data_url(), function(data) {
            draw_hist(data);
           /* draw_hist_words_added(data);
            draw_hist_words_deleted(data);*/
            draw_exp(data);
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


    function draw_exp(data) {
        // Assign the specification to a local variable vlSpec.
        var vlSpec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
            "data": {"values": data, "format": "csv"},
            "mark": "point",
            "width": 800,
            "height": 330,
            "encoding": {
              "x": {
                  "field": "unters_beginn",
                  "type": "temporal",
                  "axis": {
                      "title": "G->F distribution"
                   }
                },
              "y": {
                "field": "jaccard_g_f", "type": "quantitative",
                "axis": {
                  "title": "Similarity G->F"
                }
              },
              "color": {"value":"#ff8c00"}
            }
          };

          // Embed the visualization in the container with id `vis`
          vegaEmbed("#vis_exp", vlSpec, {"actions":false});
    }


    function draw_hist_words_added(data) {
        // Assign the specification to a local variable vlSpec.
        var vlSpec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
            "data": {"values": data, "format": "csv"},
            "mark": "bar",
            "encoding": {
              "y": {
                  "bin": {"step": 0.2},
                  "field": "words_added_g_f",
                  "type": "quantitative",
                  "axis": {
                      "title": "G->F words added"
                   }
                },
              "x": {
                "aggregate": "count", "type": "quantitative",
                "axis": {
                  "title": "#Reports"
                }
              },
              "color": {"value":"#2ca02c"}
            }
          };

          // Embed the visualization in the container with id `vis`
          vegaEmbed("#vis_w_a", vlSpec, {"actions":false});
    }

    function draw_hist_words_deleted(data) {
        // Assign the specification to a local variable vlSpec.
        var vlSpec = {
            "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
            "data": {"values": data, "format": "csv"},
            "mark": "bar",
            "encoding": {
              "y": {
                  "bin": {"step": 0.2},
                  "field": "words_deleted_g_f",
                  "type": "quantitative",
                  "axis": {
                      "title": "G->F words deleted"
                   }
                },
              "x": {
                "aggregate": "count", "type": "quantitative",
                "axis": {
                  "title": "#Reports"
                }
              },
              "color": {"value":"#d62728"}
            }
          };

          // Embed the visualization in the container with id `vis`
          vegaEmbed("#vis_w_d", vlSpec, {"actions":false});
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
              "color": {"value":"#6b486b"}
            }
          };
          // Embed the visualization in the container with id `vis`
          vegaEmbed("#vis_s_f", vlSpec, {"actions":false});
    }


    function draw_grouped() {
        var svg = d3.select("#grouped"),
            margin = { top: 20, right: 20, bottom: 20, left: 40 },
            width = +svg.attr("width") - margin.left - margin.right,
            height = +svg.attr("height") - margin.top - margin.bottom,
            g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");




        var x = d3.scaleLinear().range([0, width]).domain([0, 10]),
          y = d3.scaleLinear().range([height, 0]).domain([0, 5]);

        // Add the X Axis
        g.append("g")
          .attr("transform", "translate(0," + height + ")")
          .call(d3.axisBottom(x));

        // Add the Y Axis
        g.append("g")
          .call(d3.axisLeft(y));

         d3.csv(data_url(), function (data, columns) {
            for (var i = 1, n = columns.length; i < n; ++i) {
             console.log(columns);
            }
            return data;
        }, function (error, data) {
            if (error) throw error;

        g.selectAll(".point")
          .data(data)
          .enter()
          .append("circle")
          .attr("cx", function(d) {
            return x(d[0]);
          })
          .attr("cy", function(d) {
            return y(d[1]);
          })
          .attr("r", 4)
          .style("fill", "steelblue")
          .style("stroke", "lightgray");

        // right histogram
        var gRight = svg.append("g")
          .attr("transform",
            "translate(" + (margin.left + width) + "," + margin.top + ")");

        var yBins = d3.histogram()
          .domain(y.domain())
          .thresholds(y.ticks(5))
          .value(function(d) {
            return d[1];
          })(data);

        var yx = d3.scaleLinear()
          .domain([0, d3.max(yBins, function(d) {
            return d.length;
          })])
          .range([0, margin.right]);

        var yBar = gRight.selectAll(".bar")
          .data(yBins)
          .enter().append("g")
          .attr("class", "bar")
          .attr("transform", function(d) {
            return "translate(" + 0 + "," + y(d.x1) + ")";
          });

        var bWidth = y(yBins[0].x0) - y(yBins[0].x1) - 1;
        yBar.append("rect")
          .attr("y", 1)
          .attr("width", function(d){
            return yx(d.length);
          })
          .attr("height", bWidth)
          .style("fill", "steelblue");

        yBar.append("text")
          .attr("dx", "-.75em")
          .attr("y", bWidth / 2 + 1)
          .attr("x", function(d){
            return yx(d.length);
          })
          .attr("text-anchor", "middle")
          .text(function(d) {
            return d.length < 4 ? "" : d.length;
          })
          .style("fill", "white")
          .style("font", "9px sans-serif");
        });


       /* var x0 = d3.scaleBand()
            .rangeRound([0, width])
            .paddingInner(0.1);

        var x1 = d3.scaleBand()
            .padding(0.05);

        var y = d3.scaleLinear()
            .rangeRound([height, 0]);

        var z = d3.scaleOrdinal()
            .range(["#6b486b", "#ff8c00"]);

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
            var keys = ['jaccard_s_f', 'jaccard_g_f']
            x0.domain(data.map(function (d) { return d.unters_beginn; }));
            x1.domain(keys).rangeRound([0, x0.bandwidth()]);
            y.domain([0, d3.max(data, function (d) {
                return d3.max(keys, function (key) {
                    return d[key]; }); })]).nice();

            var div = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

            tooltipFormat = d3.timeFormat("%d.%m.%Y");
            g.append("g")
                .selectAll("g")
                .data(data)
                .enter().append("g")
                  .attr("transform", function (d) {
                      return "translate(" + x0(d.unters_beginn) + ",0)"; })
                .selectAll("rect")
                .data(function (d) {
                    return keys.map(function (key) {
                        return { key: key, value: d[key], e: d }; }); })
                .enter().append("rect")
                  .attr("x", function (d) { return x1(d.key); })
                  .attr("y", function (d) { return y(d.value); })
                  .attr("width", x1.bandwidth())
                  .attr("height", function (d) { return height - y(d.value); })
                  .attr("fill", function (d) { return z(d.key); })
                  .on("mouseover", function(d) {
                      div.transition()
                          .duration(200)
                          .style("opacity", .9);
                      div.html("<span>Similarity: " + d.value + "</span><br/>"
                               + "<span>" + d.e.untart_name + "</span><br/>"
                               + "<span>" + tooltipFormat(d.e.unters_beginn) + "</span>")
                          .style("left", (d3.event.pageX) + "px")
                          .style("top", (d3.event.pageY - 28) + "px")
                  })
                  .on("mouseout", function(d) {
                    div.transition()
                        .duration(500)
                        .style("opacity", 0);
                  })
                  .on("click", function(d) {
                      var url = 'diff/' + d.e.befund_schluessel
                      window.location = url;
                  })

            g.append("g")
                .attr("class", "axis axis--x")
                .attr("transform", "translate(0," + height + ")")
                .call(d3.axisBottom(x0).tickFormat(d3.timeFormat('%d.%m')));

            g.append("g")
                .attr("class", "axis")
                .call(d3.axisLeft(y).ticks(8, "%"))
                .append("text")
                .attr("x", 5)
                .attr("y", y(y.ticks().pop()) + 0.5)
                .attr("dy", "0.32em")
                .attr("fill", "#000")
                .attr("font-weight", "bold")
                .attr("text-anchor", "start")
                .text("Similarity index");

            var legend = g.append("g")
                .attr("font-family", "sans-serif")
                .attr("font-size", 10)
                .attr("text-anchor", "end")
                .selectAll("g")
                .data(keys.slice().reverse())
                .enter().append("g")
                .attr("transform", function (d, i) {
                    return "translate(0," + i * 20 + ")"; });

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
                    if (d === 'jaccard_s_f') {
                        return 'Schreiben vs Final';
                    } else if (d === 'jaccard_g_f') {
                        return 'Gegengelesen vs Final'
                    }
                });
        });*/
    }

    function draw_add_delete() {
        var svg = d3.select("#add_delete"),
            margin = { top: 20, right: 20, bottom: 30, left: 40 },
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
            x0.domain(data.map(function (d) { return d.unters_beginn; }));
            x1.domain(keys).rangeRound([0, x0.bandwidth()]);
            y.domain([0, d3.max(data, function (d) {
                return d3.max(keys, function (key) {
                    return d[key]; }); })]).nice();

            g.append("g")
                .selectAll("g")
                .data(data)
                .enter().append("g")
                  .attr("transform", function (d) {
                      return "translate(" + x0(d.unters_beginn) + ",0)"; })
                .selectAll("rect")
                  .data(function (d) { return keys.map(function (key) {
                      return { key: key, value: d[key] }; }); })
                  .enter().append("rect")
                    .attr("x", function (d) { return x1(d.key); })
                    .attr("y", function (d) { return y(d.value); })
                    .attr("width", x1.bandwidth())
                    .attr("height", function (d) { return height - y(d.value); })
                    .attr("fill", function (d) { return z(d.key); });

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
                    return "translate(0," + i * 20 + ")"; });

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
            margin = { top: 20, right: 20, bottom: 30, left: 40 },
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
            x0.domain(data.map(function (d) { return d.unters_beginn; }));
            x1.domain(keys).rangeRound([0, x0.bandwidth()]);
            y.domain([0, d3.max(data, function (d) {
                return d3.max(keys, function (key) {
                    return d[key]; }); })]).nice();

            g.append("g")
                .selectAll("g")
                .data(data)
                .enter().append("g")
                  .attr("transform", function (d) {
                      return "translate(" + x0(d.unters_beginn) + ",0)"; })
                .selectAll("rect")
                  .data(function (d) { return keys.map(function (key) {
                      return { key: key, value: d[key] }; }); })
                  .enter().append("rect")
                    .attr("x", function (d) { return x1(d.key); })
                    .attr("y", function (d) { return y(d.value); })
                    .attr("width", x1.bandwidth())
                    .attr("height", function (d) { return height - y(d.value); })
                    .attr("fill", function (d) { return z(d.key); });

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
                .attr("transform", function (d, i) { return "translate(0," + i * 20 + ")"; });

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