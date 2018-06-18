$(function () {
    var counter = 0;
    if ('writer-dashboard' === $('body').data('page')) {
        console.log('on writer-dashboard page');
        checkboxHandler();
        drawDivContents();
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
        return 'writer-dashboard/data?' + $.param(param)
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

        drawGraph(data, d3.select("#SimilarityGraph"), "jaccard_s_f", maxIntervalValue, minIntervalValue, classNames, color, radius, pieSegments, null);
        drawPieChart(d3.select("#SimilarityPieChartSingle"), median_single["jaccard_s_f"], "pieChartFontSingle", radius, pieSegments);
        pieSegments[0].color = "#666967";
        drawPieChart(d3.select("#SimilarityPieChartAll"), median_all["jaccard_s_f"], "pieChartFontAll", radius, pieSegments);
    }

    function drawWordsAddedGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            maxBarValue = 1,
            classNames = ["barWordsAdded", "buttonWordsAdded", "buttonAnnotationWordsAdded", "WordsAdded"],
            color = "green";
        drawGraph(data, d3.select("#WordsAddedGraph"), "words_added_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, null);
        drawBarChart(data, d3.select("#WordsAddedBarChart"), "words_added_relative_s_f", color, maxBarValue);
    }

    function drawWordsDeletedGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            maxBarValue = 1,
            classNames = ["barWordsDeleted", "buttonWordsDeleted", "buttonAnnotationWordsDeleted", "WordsDeleted"],
            color = "red";
        drawGraph(data, d3.select("#WordsDeletedGraph"), "words_deleted_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, null);
        drawBarChart(data, d3.select("#WordsDeletedBarChart"), "words_deleted_relative_s_f", color, maxBarValue);
    }

    function drawDivContents() {
        d3.csv(data_url(), function (error, data) {
            if (error) throw error;
            drawSimilarityGraph(data);
            drawWordsAddedGraph(data);
            drawWordsDeletedGraph(data);
        });
    }
});