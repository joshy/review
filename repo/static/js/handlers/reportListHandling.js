$(".examListButton").click(function () {
    $(".expandedReportList").toggle();

    if ($(this).text().trim() === "Expand List") {
        $(this).text("Hide List");

    } else if ($(this).text().trim() === "Hide List") {
        $(this).text("Expand List");
    }
});