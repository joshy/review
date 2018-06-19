$(function () {
    if ('reviewer-dashboard' === $('body').data('page')) {
        console.log('on reviewer-dashboard page');
        buttonHandler();
        checkboxHandler();
        drawDivContentsReviewer()
    }
});

var writer;

function drawWordsAddedGraphReviewer(data) {
    var maxIntervalValue = 1,
        minIntervalValue = 0,
        maxBarValue = 1,
        classNames = ["barWordsAdded", "buttonWordsAdded", "buttonAnnotationWordsAdded", "Words Added"],
        color = "green";
    if (writer != null) {
        drawGraph(data, d3.select("#WordsAddedGraph" + writer), "words_added_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, writer);
        drawBarChart(data, d3.select("#WordsAddedBarChart" + writer), "words_added_relative_s_f", color, maxBarValue);
    }
    else {
        drawBarChart(data, d3.select("#WordsAddedBarChart"), "words_added_relative_g_f", color, maxBarValue);
    }
}

function drawWordsDeletedGraphReviewer(data) {
    var maxIntervalValue = 1,
        minIntervalValue = 0,
        maxBarValue = 1,
        classNames = ["barWordsDeleted", "buttonWordsDeleted", "buttonAnnotationWordsDeleted", "Words Deleted"],
        color = "red";
    if (writer != null) {
        drawGraph(data, d3.select("#WordsDeletedGraph" + writer), "words_deleted_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, writer);
        drawBarChart(data, d3.select("#WordsDeletedBarChart" + writer), "words_deleted_relative_s_f", color, maxBarValue);
    }
    else {
        drawBarChart(data, d3.select("#WordsDeletedBarChart"), "words_deleted_relative_g_f", color, maxBarValue);
    }
}

function buttonHandler() {
    $(".writerButton").click(function () {
        writer = $(this).closest("tr")
            .find(".writerName")
            .text();
        writer = writer.slice(0, writer.indexOf(" ")).trim();
        var graphId = "#graphs" + writer;
        $(graphId).toggle();

        if ($(this).text().trim() === "Show") {
            $(this).text("Hide");
            drawDivContentsReviewer();
        } else if ($(this).text().trim() === "Hide") {
            $(this).text("Show");
            clearContent(writer);
        }
    });
}
