$(function () {
    var writer;
    if ('reviewer-dashboard' === $('body').data('page')) {
        console.log('on reviewer-dashboard page');
        buttonHandler();
        checkboxHandler();
        drawDivContents();
    }

    function data_url() {
        var reviewer = $('#reviewer').val(),
            last_exams = $('#last_exams').val(),
            start_date = $('#start_date').val(),
            end_date = $('#end_date').val(),
            departments = [];

        $.each($("input[name='departments']:checked"), function () {
            departments.push($(this).val());
        });

        var param = {
            'r': reviewer,
            'last_exams': last_exams,
            'start_date': start_date,
            'end_date': end_date,
            'departments': departments
        };
        return 'reviewer-dashboard/data?' + $.param(param)
    }

    function drawWordsAddedGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            maxBarValue = 1,
            classNames = ["barWordsAdded", "buttonWordsAdded", "buttonAnnotationWordsAdded", "WordsAdded"],
            color = "green";
        if (writer != null) {
            drawGraph(data, d3.select("#WordsAddedGraph" + writer), "words_added_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, writer);
            drawBarChart(data, d3.select("#WordsAddedBarChart" + writer), "words_added_relative_s_f", color, maxBarValue);
        }
        else {
            drawBarChart(data, d3.select("#WordsAddedBarChart"), "words_added_relative_g_f", color, maxBarValue);
        }
    }

    function drawWordsDeletedGraph(data) {
        var maxIntervalValue = 1,
            minIntervalValue = 0,
            maxBarValue = 1,
            classNames = ["barWordsDeleted", "buttonWordsDeleted", "buttonAnnotationWordsDeleted", "WordsDeleted"],
            color = "red";
        if (writer != null) {
            drawGraph(data, d3.select("#WordsDeletedGraph" + writer), "words_deleted_relative_s_f", maxIntervalValue, minIntervalValue, classNames, color, maxBarValue, null, writer);
            drawBarChart(data, d3.select("#WordsDeletedBarChart" + writer), "words_deleted_relative_s_f", color, maxBarValue);
        }
        else {
            drawBarChart(data, d3.select("#WordsDeletedBarChart"), "words_deleted_relative_g_f", color, maxBarValue);
        }
    }

    function drawDivContents() {
        d3.csv(data_url(), function (error, data) {
            if (error) throw error;
            drawWordsAddedGraph(data);
            drawWordsDeletedGraph(data);
        });
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
                drawDivContents();
            } else if ($(this).text().trim() === "Hide") {
                $(this).text("Show");
                clearContent(writer);
            }
        });
    }
});