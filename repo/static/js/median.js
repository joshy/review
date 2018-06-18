function calculateMedian(data, value) {
    var valueList = data.map(function (d) {
        return parseFloat(d[value]);
    });

    return _calculateMedian(valueList);
}

function _calculateMedian(values) {

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