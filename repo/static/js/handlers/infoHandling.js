$(".infoDashboard").hover(
    function () {
        $(this).append($("<span>: The Dashboard visualizes the similarity calculation between three different states of each report: <br>" +
            "<b>&#39schreiben&#39, &#39gegengelesen&#39 and &#39final&#39</b> <br>"+
            "The similarities between <b>&#39schreiben -> final&#39 and &#39gegengelesen -> final&#39</b> have been calculated <br>"+
            "and can be compared using the dashboard. The calculation have been measured by means of the <b>Jaccard-Index</b>.</span>"));
    }, function () {
        $(this).find("span:last").remove();
    });

$(".infoReportsList").hover(
    function () {
        $(this).append($("<span>: The List below shows the latest five reports which have been concluded with status final <br>" +
            "Click on <b>&#39Show changes&#39</b> at the end of each row to see the particular report <br>" +
            "<b>s->f: &#39schreiben -> final&#39 / g->f: &#39gegengelesen -> final&#39</b></span>"));
    }, function () {
        $(this).find("span:last").remove();
    });

$(".infoSimilarity").hover(
    function () {
        $(this).append($("<span>: The following graph shows the <b>Similarity-Value</b> of each concluded report over time. Click on a specific circle to see the report<br>" + "" +
            "Click on the button at the top right corner to switch between <b>&#39schreiben -> final&#39 and &#39gegenlesen -> final&#39</b> <br>" +
            "Click on a specific histogram interval to see a detailed view, by clicking the third time the graph will be reset.  </span>"));
    }, function () {
        $(this).find("span:last").remove();
    });

$(".infoWordsAdded").hover(
    function () {
        $(this).append($("<span>: The following graph shows the <b>relative amount of all added words of each concluded report over time</b>. Click on a specific<br>" + "" +
            "circle to see the report. Click on the button at the top right corner to switch between <b>&#39schreiben -> final&#39 and &#39gegenlesen -> final&#39</b> <br>" +
            "Click on a specific histogram interval to see a detailed view, by clicking the third time the graph will be reset.  </span>"));
    }, function () {
        $(this).find("span:last").remove();
    });

$(".infoWordsDeleted").hover(
    function () {
        $(this).append($("<span>: The following graph shows the <b>relative amount of all deleted words of each concluded report over time</b>. Click on a specific<br>" + "" +
            "circle to see the report. Click on the button at the top right corner to switch between <b>&#39schreiben -> final&#39 and &#39gegenlesen -> final&#39</b> <br>" +
            "Click on a specific histogram interval to see a detailed view, by clicking the third time the graph will be reset.  </span>"));
    }, function () {
        $(this).find("span:last").remove();
    });

$(".infoMedian").hover(
    function () {
        $(this).append($("<span>: The following graph shows your <b>personal calculated Median</b> over the specified reports and the <b>calculated Median over all reports</b>. <br>" +
            "By clicking on the botton at the top right corner of the specific graph you can switch between <b>&#39schreiben -> final&#39 and &#39gegenlesen -> final&#39</b> values. </span>"));
    }, function () {
        $(this).find("span:last").remove();
    });