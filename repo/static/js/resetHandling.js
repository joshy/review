function clearContent(writer) {
    d3.select("#WordsAddedBarChart" + writer).selectAll("g").remove();
    d3.select("#WordsDeletedBarChart" + writer).selectAll("g").remove();
    d3.select("#WordsAddedGraph" + writer).selectAll("g").remove();
    d3.select("#WordsDeletedGraph" + writer).selectAll("g").remove();
    d3.selectAll(".tooltip").remove();
}

function clearAllContent() {
    d3.selectAll("svg").selectAll("g").remove();
    d3.selectAll(".tooltip").remove();
}