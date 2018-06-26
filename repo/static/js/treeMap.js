$(function () {
    if ('treeMap' === $('body').data('page')) {
        selectionHandler();
    }

});

function treeMapModuleLoaded() {
    com.macrofocus.treemap.TreeMap.setLicenseKey("Kevin Streiter",
        "TG2GS-W57BU-4CLVB-866AK-QQFBT-DGV3W");
    treeMap = new com.macrofocus.treemap.TreeMap("treeMap");
    treeMap.loadJavaScriptArray(rows)
}

function treeMapModelLoaded() {
    treeMap.setToolTipByNames("befund_freigabe", "schreiber", "freigeber", "jaccard_s_f", "jaccard_g_f",
        "words_added_relative_s_f", "words_added_relative_g_f", "words_deleted_relative_s_f", "words_deleted_relative_g_f");
    treeMap.setColorByName($('.selectValue option:selected').val());
    setGroupByByNames();
    treeMap.setRendering(com.macrofocus.treemap.RenderingFactory.FLAT_NO_BORDER);
    var treeMapModel = treeMap.getModel();
    var treeMapSettings = treeMapModel.getSettings();
    var fieldSettings = treeMapSettings.getDefaultFieldSettings();
    fieldSettings.setAlgorithm(com.macrofocus.treemap.AlgorithmFactory.SQUARIFIED);
}

function selectionHandler() {
    $('.selectValue').change(function () {
        var selection = $(".selectValue option:selected").val();
        treeMap.setColorByName(selection);
    });
    $('.selectGroup').change(function () {
        setGroupByByNames();
    });
}

function setGroupByByNames() {
    var selection = $(".selectGroup option:selected").val();
    var selectionParts = selection.split(",", 3);
    selectionParts = selectionParts.map(function (part) {
        return part.trim();
    });

    switch (selectionParts.length) {
        case 0:
            break;
        case 1:
            treeMap.setGroupByByNames(selectionParts[0]);
            break;
        case 2:
            treeMap.setGroupByByNames(selectionParts[0], selectionParts[1]);
            break;
        case 3:
            treeMap.setGroupByByNames(selectionParts[0], selectionParts[1], selectionParts[2]);
    }
}
