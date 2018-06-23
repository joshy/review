$(function () {
    if ('writer-dashboard' === $('body').data('page')) {
        console.log('on writer-dashboard page');
        checkboxHandler();
        drawDivContentsWriter();
    }
});

function drawSimilarityGraphWriter() {
    var maxIntervalValue = 1,
        minIntervalValue = 0,
        pieSegments = [
            {name: 'medianValue', value: 0.0, color: "steelblue"},
            {name: 'maxValue', value: 0.0, color: 'lightgrey'},
        ],
        classNames = ["barSimilarity", "buttonSimilarity", "buttonAnnotationSimilarity", "Similarity"],
        color = "steelblue",
        radius = 150;

    drawGraph(d3.select("#SimilarityGraph"), "jaccard_s_f", maxIntervalValue, minIntervalValue, classNames, color, radius, pieSegments, null);
    drawPieChart(d3.select("#SimilarityPieChartSingle"), data["median_single"]["jaccard_s_f"], "pieChartFontSingle", radius, pieSegments);
    pieSegments[0].color = "#666967";
    drawPieChart(d3.select("#SimilarityPieChartAll"), data["median_all"]["jaccard_s_f"], "pieChartFontAll", radius, pieSegments);
}

function drawWordsAddedGraphWriter() {
    var maxIntervalValue = 1,
        minIntervalValue = 0,
        maxBarValue = 1,
        classNames = ["barWordsAdded", "buttonWordsAdded", "buttonAnnotationWordsAdded", "Words Added"],
        color = "green";
    drawGraph(d3.select("#WordsAddedGraph"), "words_added_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, null);
    drawBarChart(d3.select("#WordsAddedBarChart"), "words_added_relative_s_f", color, maxBarValue, null);
}

function drawWordsDeletedGraphWriter() {
    var maxIntervalValue = 1,
        minIntervalValue = 0,
        maxBarValue = 1,
        classNames = ["barWordsDeleted", "buttonWordsDeleted", "buttonAnnotationWordsDeleted", "Words Deleted"],
        color = "red";
    drawGraph(d3.select("#WordsDeletedGraph"), "words_deleted_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, null);
    drawBarChart(d3.select("#WordsDeletedBarChart"), "words_deleted_relative_s_f", color, maxBarValue, null);
}