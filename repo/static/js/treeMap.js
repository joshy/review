$(function () {
    if ('treeMap' === $('body').data('page')) {
    }

});

function treeMapModuleLoaded() {
    console.log(rows);
    com.macrofocus.treemap.TreeMap.setLicenseKey("Kevin Streiter",
        "TG2GS-W57BU-4CLVB-866AK-QQFBT-DGV3W");
    treeMap = new com.macrofocus.treemap.TreeMap("treeMap");
    treeMap.loadJavaScriptArray(rows)
}

function treeMapModelLoaded() {
    treeMap.setToolTipByNames("befund_freigabe", "schreiber", "freigeber", "jaccard_s_f", "jaccard_g_f",
        "words_added_relative_s_f", "words_added_relative_g_f", "words_deleted_relative_s_f", "words_deleted_relative_g_f");
    treeMap.setColorByName("jaccard_g_f");
    treeMap.setGroupByByNames("pp_misc_mfd_1_kuerzel", "schreiber");
    var treeMapModel = treeMap.getModel();
    var treeMapSettings = treeMapModel.getSettings();
    var fieldSettings = treeMapSettings.getDefaultFieldSettings();
    fieldSettings.setAlgorithm(com.macrofocus.treemap.AlgorithmFactory.SQUARIFIED);
}
