function clearContent(operator) {
    d3.select("#WordsAddedBarChart" + operator).selectAll("g").remove();
    d3.select("#WordsDeletedBarChart" + operator).selectAll("g").remove();
    d3.select("#WordsAddedGraph" + operator).selectAll("g").remove();
    d3.select("#WordsDeletedGraph" + operator).selectAll("g").remove();
    d3.selectAll(".tooltip").remove();
}

function clearAllContent() {
    d3.selectAll("svg").selectAll("g").remove();
    d3.selectAll(".tooltip").remove();
}
