function drawDivContentsWriter() {
    d3.csv(dataUrl('writer'), function (error, data) {
        if (error) throw error;
        drawSimilarityGraphWriter(data);
        drawWordsAddedGraphWriter(data);
        drawWordsDeletedGraphWriter(data);
    });
}

function drawDivContentsReviewer() {
    d3.csv(dataUrl('reviewer'), function (error, data) {
        if (error) throw error;
        drawWordsAddedGraphReviewer(data);
        drawWordsDeletedGraphReviewer(data);
    });
}

function dataUrl(operator) {
    var operatorName = $('#'+operator).val(),
        last_exams = $('#last_exams').val(),
        start_date = $('#start_date').val(),
        end_date = $('#end_date').val(),
        departments = [];

    $.each($("input[name='departments']:checked"), function () {
        departments.push($(this).val());
    });

    var param = {
        'last_exams': last_exams,
        'start_date': start_date,
        'end_date': end_date,
        'departments': departments
    };
    param[operator.charAt(0)] = operatorName;
    return operator+'-dashboard/data?' + $.param(param)
}